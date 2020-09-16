from django.conf import settings
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

THROTTLES = settings.API['throttles']

class SustainedRateAnonThrottle(AnonRateThrottle):
    scope = 'anon-sustained'
    rate = THROTTLES['sustain_anon']

class BurstRateAnonThrottle(AnonRateThrottle):
    scope = 'anon-burst'
    rate = THROTTLES['burst_anon']

class SustainedRateUserThrottle(UserRateThrottle):
    scope = 'user-sustained'
    rate = THROTTLES['sustain_user']

class BurstRateUserThrottle(UserRateThrottle):
    scope = 'user-burst'
    rate = THROTTLES['burst_user']
