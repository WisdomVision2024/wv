from rest_framework import serializers
from .models import userdata


from django.contrib.auth.hashers import check_password
class userdataSerializer(serializers.ModelSerializer):
    class Meta:
        model = userdata
        fields = ('Name','Password','Identity','Phone','Email')
    
def login_user(Phone,Password):
        try:
            user = userdata.objects.get(Phone = Phone)
            
            if Password == user.Password:
                return {
                    "Phone":user.Phone,
                    "Password":user.Password,
                    "Name": user.Name,
                    "Identity":user.Identity,
                    "Email":user.Email,
                    "success": True,
                    "errorMessage": "login!!!"
                    }              
            else:
                return {
                "success": False,
                "errorMessage": "密碼錯誤"
                }
        
        except userdata.DoesNotExist:
            return {
            "success": False,
            "errorMessage": "尚未註冊"
        }
    
def register_user(cPhone,cPassword,cName,cEmail,cIdentity):
    if not cPhone:
        return {"success": False, "errorMessage": "Phone number cannot be empty"}
    if not cName:
        return {"success": False, "errorMessage": "Username cannot be empty"}
    if not cPassword:
        return {"success": False, "errorMessage": "Password cannot be empty"}
    
    
        
    if userdata.objects.filter(Phone=cPhone).exists():
        return{"success": False, "errorMessage": "PhoneNumber already exists"}
        
    if userdata.objects.filter(Name=cName).exists():
        return{"success": False, "errorMessage": "Username already exists"}

    user = userdata.objects.create(
        Name=cName,
        Phone=cPhone,
        Password=cPassword,
        Identity=cIdentity,
        Email=cEmail,
     )

    user.save()
    return {"success": True, "errorMessage": "User created successfully"}


        
def update_account(Phone, newName, newEmail, oldPassword, newPassword):
    try:
        # 查找使用者
        user = userdata.objects.get(Phone=Phone)
        
        # 更新帳號資訊
        if newName:
            user.Name = newName
        if newEmail:
            user.Email = newEmail

        # 檢查舊密碼是否正確
        if oldPassword and oldPassword != user.Password:
            return {
                "success": False,
                "errorMessage": "舊密碼不正確"
            }

        # 更新密碼（如果有提供新密碼）
        if newPassword:
            user.Password = newPassword
            user.save()  # 保存所有更新
            
            return {
                "success": True,
                "errorMessage": "帳號資訊與密碼更新成功",
                "Phone": user.Phone,
                "Name": user.Name,
                "Email": user.Email,
            }
        else:
            # 如果沒有提供新密碼，只更新帳號資訊
            user.save()  # 保存帳號更新
            return {
                "success": True,
                "errorMessage": "帳號資訊更新成功",
                "Phone": user.Phone,
                "Name": user.Name,
                "Email": user.Email,
            }

    except userdata.DoesNotExist:
        return {
            "success": False,
            "errorMessage": "帳號不存在"
        }