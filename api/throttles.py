from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class SustainedRateAnonThrottle(AnonRateThrottle):
    scope = 'anon-sustained'
    rate = '50/day'

class BurstRateAnonThrottle(AnonRateThrottle):
    scope = 'anon-burst'
    rate = '20/hour'

class SustainedRateUserThrottle(UserRateThrottle):
    scope = 'user-sustained'
    rate = '200/day'

class BurstRateUserThrottle(UserRateThrottle):
    scope = 'user-burst'
    rate = '50/hour'
