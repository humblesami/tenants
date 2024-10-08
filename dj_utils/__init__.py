from django.db import transaction, router
from django.contrib import admin, messages
from django.http import HttpResponseRedirect


def next_prev_id(model, row_id):
    prev_obj = model.objects.filter(pk__lt=row_id).order_by("-pk").first()
    next_obj = model.objects.filter(pk__gt=row_id).order_by("pk").first()
    output = {"prev": "", "next": "", "current": row_id}
    prev_pk = 0
    next_pk = 0

    rec_count = 0
    if not prev_obj or not next_obj:
        rec_count = model.objects.all().count()

    if prev_obj:
        prev_pk = prev_obj.pk
        output['prev'] = prev_pk
    else:
        if rec_count > 1:
            obj = model.objects.order_by("-pk").first()
            if obj:
                prev_pk = obj.pk
                if prev_pk != row_id:
                    output['prev'] = prev_pk

    if next_obj:
        next_pk = next_obj.pk
        output['next'] = next_pk
    else:
        if rec_count > 1:
            obj = model.objects.all().order_by("pk").first()
            if obj:
                next_pk = obj.pk
                if next_pk != row_id:
                    output['next'] = next_pk
    return output


class NavigateFormAdmin(admin.ModelAdmin):
    save_on_top = True

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if obj and obj.pk:
            ids = next_prev_id(obj._meta.model, obj.pk)
            context['npc_ids'] = ids
        res = super().render_change_form(request, context, add, change, form_url)
        return res

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            with transaction.atomic(using=router.db_for_write(self.model)):
                return self._changeform_view(request, object_id, form_url, extra_context)
        except Exception as e:
            self.message_user(request, e, level=messages.ERROR)
            return HttpResponseRedirect(request.path)


admin.ModelAdmin = NavigateFormAdmin
