from rest_framework.throttling import UserRateThrottle


class ReviewCreateTrottle(UserRateThrottle):
    scope = 'review-create'


class ReviewListTrottle(UserRateThrottle):
    scope = 'review-list'
