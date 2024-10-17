from django.db import models
from py_utils.helpers import HttpUtils


class LoginLocation(models.Model):
    country = models.CharField(max_length=128, null=True)
    city = models.CharField(max_length=128, null=True)
    zip = models.CharField(max_length=16, null=True)
    region = models.CharField(max_length=128, null=True)
    longitude = models.CharField(max_length=16, null=True)
    latitude = models.CharField(max_length=16, null=True)
    time_zone = models.CharField(max_length=64, null=True)
    ip = models.GenericIPAddressField(null=True)


class LoginEntry(models.Model):
    name = models.CharField(max_length=64, null=True)
    user_id = models.IntegerField(null=True)
    location = models.ForeignKey(LoginLocation, null=True, on_delete=models.SET_NULL)
    path_info = models.CharField(max_length=64, null=True)
    operating_system = models.CharField(max_length=32, null=True)
    login_time = models.DateTimeField(auto_now_add=True, null=True)
    browser = models.CharField(max_length=123, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_last_login_info(cls, user_id):
        entry = LoginEntry.objects.filter(user_id=user_id).order_by('-id')
        if entry:
            entry = entry[0]
            location = {
                'city': entry.location.city,
                'country': entry.location.country,
                'region': entry.location.region,
                'zip': entry.location.zip,
                'longitude': entry.location.longitude,
                'latitude': entry.location.latitude,
                'ip': entry.location.ip,
            }

            entry = {
                'operating_system': entry.operating_system,
                'location': location,
                'login_time': str(entry.login_time),
                'browser': entry.browser
            }
            if location['country'] or location['longitude']:
                entry['has_location'] = 1
            return entry
        else:
            return 'No login info'


def make_login_entry(request, user):
    meta = request.META
    ip = HttpUtils.get_client_ip(request.META)
    operating_system = meta.get('SESSION')
    time_zone = meta.get('TZ')
    agent = meta.get('HTTP_USER_AGENT')
    browser = HttpUtils.get_browser(agent)
    path_info = meta.get('PATH_INFO')
    res = HttpUtils.get_location_from_ip(ip)
    location = LoginLocation.objects.filter(
        time_zone=time_zone,
        ip=ip,
        country=res.get('country_name'),
        city=res.get('city'),
        zip=res.get('zip'),
        region=res.get('region_name'),
        longitude=res.get('longitude'),
        latitude=res.get('latitude')
    ).first()
    if not location:
        location = LoginLocation.objects.create(
            time_zone=time_zone,
            ip=ip,
            country=res.get('country_name'),
            city=res.get('city'),
            zip=res.get('zip'),
            region=res.get('region_name'),
            longitude=res.get('longitude'),
            latitude=res.get('latitude')
        )

    login_entry = LoginEntry(
        location_id=location.id,
        user_id=user.id,
        browser=browser,
        name=str(user.id) + '-' + ip,
        operating_system=operating_system,
    )
    if path_info != '/rest/public':
        login_entry.path_info = path_info
    login_entry.save()

