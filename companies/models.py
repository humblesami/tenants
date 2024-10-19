from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django_tenants.models import DomainMixin, TenantMixin

from py_utils.helpers import DateUtils
from .tools import switch_tenant


class AppModule(models.Model):
    app_name = models.CharField(max_length=63)
    description = models.CharField(max_length=1023)
    is_active = models.BooleanField(default=True)
    base_cost = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = '01. Tenant Apps'

    def __str__(self):
        return self.app_name


class Duration(models.Model):
    days = models.IntegerField(default=1)
    cost_factor = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = '02. Package Days'

    def __str__(self):
        return str(self.days)


class UserWindow(models.Model):
    window_name = models.CharField(max_length=31, unique=True)
    min_user_count = models.IntegerField(default=1)
    max_user_count = models.IntegerField(default=1, unique=True)
    cost_factor = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = '03. User Limit Windows'

    def __str__(self):
        return self.window_name


class AppCost(models.Model):
    app_module = models.ForeignKey(AppModule, on_delete=models.RESTRICT)
    duration = models.ForeignKey(Duration, on_delete=models.RESTRICT)
    user_window = models.ForeignKey(UserWindow, on_delete=models.RESTRICT)
    cost = models.IntegerField()

    class Meta:
        verbose_name_plural = '04. App Costs'

    def __str__(self):
        return f'{self.app_module.app_name}-{self.duration.days}-{self.user_window.window_name}'


class ClientUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    client_email = models.EmailField(unique=True)
    client_image = models.ImageField(null=True, blank=True, upload_to="client_logos/%Y/%m/%d/")
    schema_name = models.CharField(max_length=63, unique=True)
    client_name = models.CharField(max_length=127)
    demo_used = models.BooleanField(default=False)
    balance = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = '05. Potential Clients'

    def __str__(self):
        return f'{self.client_name}-{self.schema_name}'


class ClientTenant(TenantMixin):
    owner = models.OneToOneField(ClientUser, on_delete=models.RESTRICT, unique=True)
    is_active = models.BooleanField(default=True, blank=True)
    users = models.ManyToManyField(User, related_name='tenants', blank=True)
    featured = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    auto_create_schema = True
    auto_drop_schema = True
    creating_tenant = 0

    class Meta:
        verbose_name_plural = '07. Client Tenants'
        ordering = ('-featured', '-updated_at')

    def __str__(self):
        return f"{self.owner.client_name}"

    def save(self, verbosity=1, *args, **kwargs):
        if not self.pk:
            schema_name = ClientTenant.objects.filter(schema_name=self.schema_name)
            if not schema_name:
                self.creating_tenant = 1
        return super().save(verbosity=1, *args, **kwargs)

    def create_schema(self, check_if_exists=False, sync_schema=True, verbosity=1):
        res = super().create_schema(check_if_exists=check_if_exists, sync_schema=sync_schema)
        if self.creating_tenant:
            self.creating_tenant = 0
            switch_tenant(self.schema_name)
            new_user = User.objects.create(
                username=self.owner.client_email, email=self.owner.client_email, is_staff=True,
                is_active=True, is_superuser=True
            )
            # tobe changed
            new_user.set_password('123')
            new_user.save()
            switch_tenant('public')
        return res


class Subscription(models.Model):
    client_user = models.ForeignKey(ClientUser, on_delete=models.RESTRICT)
    chosen_apps = models.ManyToManyField(AppModule)
    user_window = models.ForeignKey(UserWindow, on_delete=models.RESTRICT)
    duration = models.ForeignKey(Duration, on_delete=models.RESTRICT)
    discount = models.FloatField(default=0)
    cost = models.IntegerField(default=0)
    is_demo = models.BooleanField(default=False)
    request_time = models.DateTimeField(auto_now=True)
    client_tenant = models.ForeignKey(ClientTenant, on_delete=models.SET_NULL, null=True, blank=True)
    activation_time = models.DateTimeField(null=True, blank=True)
    discounted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.CharField(max_length=511, null=True, blank=True)

    class Meta:
        verbose_name_plural = '06. Subscriptions'

    def __str__(self):
        return f"{self.client_user.client_name.title()} -- {DateUtils.string_format('', self.request_time)}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.is_demo:
            if self.client_user.demo_used:
                raise Exception(f' This user already have used demo')
        if self.discount:
            if not self.remarks:
                raise Exception('There must be remarks for discount')
            if not self.discounted_by:
                raise Exception('There must be user log for discount')

        super().save(
            force_insert=force_insert, force_update=force_update,
            using=using, update_fields=update_fields
        )
        if self.is_demo and not self.client_tenant:
            create_tenant(self)
            self.client_user.demo_used = True
            self.client_user.save()

    def calculate_cost(self):
        total_cost = 0
        for item in self.chosen_apps.objects.all():
            module_cost = AppCost.objects.filter(
                duration_id=self.duration.pk,
                user_window_id=self.duration.pk,
                app_module_id=item.pk,
            ).first()
            total_cost += module_cost.cost if module_cost else 0
        total_cost -= total_cost * self.discount/100
        return total_cost


class PaymentMethod(models.Model):
    name = models.CharField(max_length=63)

    class Meta:
        verbose_name_plural = '08. Payment Methods'

    def __str__(self):
        return self.name


class Payment(models.Model):
    amount = models.PositiveIntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '09. Payments'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = self.subscription.client_user
        user.balance += self.amount
        user.save()

        cost = self.subscription.calculate_cost()
        if user.balance + self.amount <= cost:
            raise Exception(f' You still need to pay {cost - user.balance} to activate your subscription')
        super().save(
            force_insert=force_insert, force_update=force_update,
            using=using, update_fields=update_fields
        )
        create_tenant(self.subscription)
        user.balance -= self.amount
        user.save()


def create_tenant(sub_obj):
    sub_user = sub_obj.client_user
    ct = ClientTenant.objects.filter(owner_id=sub_user.pk).first()
    if not ct:
        obj = ClientTenant.objects.create(
            owner=sub_user,
            is_active=True,
            schema_name=sub_user.schema_name,
        )
        domain_value = sub_user.schema_name+'.'+settings.PUBLIC_DOMAIN
        Domain.objects.create(
            domain=domain_value,
            tenant_id=obj.pk
        )
        sub_obj.client_tenant = obj
        sub_obj.activation_time = datetime.now(tz=timezone.utc)
        sub_obj.save()
    return ct


class Domain(DomainMixin):
    pass


@receiver(post_save, sender=AppModule)
@receiver(post_save, sender=Duration)
@receiver(post_save, sender=UserWindow)
def create_or_update_app_cost(sender, instance, created, **kwargs):

    durations = Duration.objects.filter(pk=instance.pk) if sender == Duration else Duration.objects.all()
    user_windows = UserWindow.objects.filter(pk=instance.pk) if sender == UserWindow else UserWindow.objects.all()
    app_modules = AppModule.objects.filter(pk=instance.pk) if sender == AppModule else AppModule.objects.all()

    for item1 in app_modules:
        for item2 in user_windows:
            for item3 in durations:
                app_cost = AppCost.objects.filter(app_module=item1, user_window=item2, duration=item3)
                if not app_cost:
                    cost = item1.base_cost * item2.cost_factor * item3.cost_factor
                    AppCost.objects.create(app_module=item1, user_window=item2, duration=item3, cost=cost)

@receiver(pre_save, sender=AppModule)
@receiver(pre_save, sender=Duration)
@receiver(pre_save, sender=UserWindow)
def update_existing_app_costs(sender, instance, **kwargs):
    if instance.pk:
        if not AppModule or not Duration or not UserWindow:
            return
        durations = Duration.objects.filter(pk=instance.pk) if sender == Duration else Duration.objects.all()
        user_windows = UserWindow.objects.filter(pk=instance.pk) if sender == UserWindow else UserWindow.objects.all()
        app_modules = AppModule.objects.filter(pk=instance.pk) if sender == AppModule else AppModule.objects.all()

        for item1 in app_modules:
            for item2 in user_windows:
                for item3 in durations:
                    app_cost = AppCost.objects.filter(app_module=item1, user_window=item2, duration=item3).first()
                    if not app_cost:
                        continue
                    old_cost = app_cost.cost
                    new_cost = app_cost.cost
                    if sender == AppModule:
                        new_cost = old_cost * (instance.base_cost / item1.base_cost)
                    elif sender == UserWindow:
                        new_cost = old_cost * (instance.cost_factor / item2.cost_factor)
                    elif sender == Duration:
                        new_cost = old_cost * (instance.cost_factor / item3.cost_factor)
                    if old_cost != new_cost:
                        app_cost.cost = new_cost
                        app_cost.save()
