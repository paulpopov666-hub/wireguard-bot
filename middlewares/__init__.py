from .Throttling import *
from .MembershipCheck import *
from loader import dp


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(MembershipCheckMiddleware())
