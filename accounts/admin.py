from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email", "name", "password"]

    # def clean_password2(self):  # 비밀번호와 비밀번호 확인 필드가 일치하는지 검증.
    #     # Check that the two password entries match
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise ValidationError("Passwords don't match")
    #     return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)   # 객체를 생성하지만, 아직 데이터베이스에 저장은 하지 않음.
        user.set_password(self.cleaned_data["password1"])   # 입력된 비밀번호를 해시하여 저장함.
        if commit:
            user.save() # 사용자 객체를 데이터베이스에 저장함.
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()  # 비밀번호 필드를 읽기 전용으로 설정, 비밀번호를 직접 변경하지 않고 해시된 형태로 표시.

    class Meta:
        model = User
        fields = ["username", "email", "password", "profile_image", "name", "phone_number", "address", "zipcode", "is_active", "is_admin"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm # 사용자 정보 변경 및 생성에 사용할 폼을 지정함.

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["id", "username", "email", "name", "is_admin", "is_active"] # 사용자 목룍에 표시할 필드를 지정.
    list_filter = ["is_admin"]  # 사용자를 필터링할 수 있는 필터 옵션을 설정함.
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "username",
                    "email",
                    "name",
                    "password",
                ]
            },
        ),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email", "name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["username"]
    ordering = ["username"]
    filter_horizontal = []


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)