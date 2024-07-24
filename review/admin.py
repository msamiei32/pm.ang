from django.contrib import admin
from .models import ReviewTask, Review, Part, Machine


class ReviewAdmin(admin.ModelAdmin):
    # readonly_fields = ('last_sms',)
    pass

admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewTask)
admin.site.register(Part)
admin.site.register(Machine)
# Register your models here.
