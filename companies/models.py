from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django_tenants.models import DomainMixin, TenantMixin

from .tools import switch_tenant


# public admin will add only optional apps from tenant_apps in this model
class AppModule(models.Model):
    app_name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)


class UserWindow(models.Model):
    window_name = models.CharField(max_length=32, unique=True)
    min_user_count = models.IntegerField(default=1)
    max_user_count = models.IntegerField(default=1, unique=True)

# Just to define app cost per user_window for calculating cost in subscription
class AppCost(models.Model):
    app_module = models.ForeignKey(AppModule, on_delete=models.RESTRICT)
    user_window = models.ForeignKey(UserWindow, on_delete=models.RESTRICT)
    amount = models.IntegerField(default=0)


class ClientUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    client_email = models.EmailField(unique=True)
    client_password = models.CharField(max_length=128)  # Store hash here, or remove this field
    client_image = models.ImageField(null=True, blank=True, upload_to="client_logos/%Y/%m/%d/")

    def save(self, *args, **kwargs):
        if not self.user:  # Create user in public schema if not already linked
            public_user = User.objects.create(username=self.client_email, email=self.client_email, is_active=True)
            public_user.set_password(self.client_password)  # Set hashed password
            public_user.save()
            self.user = public_user
        super().save(*args, **kwargs)

# Signal to handle User creation separately if needed
@receiver(pre_save, sender=ClientUser)
def create_public_user(sender, instance, **kwargs):
    if not instance.user:  # Check if the user field is empty
        public_user = User(username=instance.client_email, email=instance.client_email, is_active=True)
        public_user.set_password(instance.client_password)
        public_user.save()
        instance.user = public_user


class ClientTenant(TenantMixin):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT, unique=True)
    is_active = models.BooleanField(default=True, blank=True)
    users = models.ManyToManyField(User, related_name='tenants', blank=True)
    featured = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    auto_create_schema = True
    auto_drop_schema = True
    creating_tenant = 0

    class Meta:
        ordering = ('-featured', '-updated_at')

    def __str__(self):
        return f"{self.client_name}"

    def save(self, verbosity=1, *args, **kwargs):
        if not self.pk:
            schema_name = ClientTenant.objects.filter(schema_name=self.schema_name)
            if schema_name:
                raise Exception(f'Schema name {self.schema_name} already exists')
            else:
                self.creating_tenant = 1
            if not self.client_name:
                self.client_name = self.schema_name
        return super().save(verbosity=1, *args, **kwargs)


    def create_schema(self, check_if_exists=False, sync_schema=True, verbosity=1):
        res = super().create_schema(check_if_exists=check_if_exists, sync_schema=sync_schema)
        if self.creating_tenant:
            self.creating_tenant = 0
            switch_tenant(self.schema_name)
            new_user = User.objects.create(
                username=self.owner.email, email=self.owner.email, is_staff=True,
                is_active=True, is_superuser=True
            )
            new_user.set_password(self.client_password)
            new_user.save()
            switch_tenant('public')
        return res


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    chosen_apps = models.ManyToManyField(AppModule)
    user_window = models.ForeignKey(UserWindow, on_delete=models.CASCADE)
    approved = models.BooleanField(verbose_name='Request Status')
    client_tenant = models.ForeignKey(ClientTenant, on_delete=models.RESTRICT, null=True, blank=True)
    cost = models.IntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        total_cost = 0
        for item in self.chosen_apps.all():
            app_cost = AppCost.filter(app_id=item.pk, user_window=self.user_window).first()
            total_cost += app_cost.amount if app_cost else 0
        if self.pk:
            being_approved = self.approved and not Subscription.objects.filter(pk=self.pk).first().approved
        else:
            being_approved = self.approved
        if being_approved:
            client_tenant = ClientTenant.objects.filter(owner_id=self.user.pk).first()
            if not client_tenant:
                client_tenant = ClientTenant.objects.create(owner=self.user)
            self.client_tenant =client_tenant
        super().save(
            force_insert=force_insert, force_update=force_update,
            using=using, update_fields=update_fields
        )


class Domain(DomainMixin):
    pass
