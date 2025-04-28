from django.contrib import admin
from .models import User, Company, Manager, Customer, Cargo

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Manager)
admin.site.register(Customer)
admin.site.register(Cargo)