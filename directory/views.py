
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from .models import Area, Member, FamilyMember
from django.db.models import Q
from django.contrib import messages
def smart_login(request):
    if request.method == "POST":
        phone = request.POST.get('phone_number', '').strip()
        
        # 1. Debug: Dekhte hain form se kya number aaya
        print(f"👉 DEBUG 1: Input Phone from Form = '{phone}'")

        # Sirf digits nikalna (space, +91, ya zero sab saaf karne ke liye)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if len(clean_phone) >= 10:
            clean_phone = clean_phone[-10:]
            
        # 2. Debug: Dekhte hain safai ke baad 10 digit kya bane
        print(f"👉 DEBUG 2: Cleaned 10-Digit Phone = '{clean_phone}'")

        # Agar number khali nahi hai toh database mein check karenge
        if clean_phone:
            # Exact match lagate hain direct phone_number field par
            member = Member.objects.filter(phone_number=clean_phone).first()
            
            # 3. Debug: Dekhte hain Django ne sahi mein dhoonda ya nahi
            print(f"👉 DEBUG 3: Database Query Result = {member}")
            if member:
                print(f"👉 DEBUG 4: Matching Member Found! ID: {member.id}, Name: {member.name}, Phone: {member.phone_number}")
                return redirect('profile_view', member_id=member.id)
            
        request.session['temp_phone'] = clean_phone
        return redirect('register')
            
    return render(request, 'home.html')
def register(request):
    areas = Area.objects.all()
    return render(request, 'register.html', {'areas': areas})
def update_member(request, id):
    member = get_object_or_404(Member, id=id)
    if request.method == "POST":
        member.name = request.POST.get('name')
        member.phone_number = request.POST.get('phone_number')
        member.dob = request.POST.get('dob') or None
        member.marital_status = request.POST.get('marital_status')
        member.gotra = request.POST.get('gotra')
        member.detailed_address = request.POST.get('detailed_address')
        member.pin = request.POST.get('pin')

        member.spouse_name = request.POST.get('spouse_name')
        member.spouse_phone = request.POST.get('spouse_phone')
        member.spouse_dob = request.POST.get('spouse_dob') or None
        
        area_id = request.POST.get('area')
        if area_id:
            try:
                member.area = Area.objects.get(id=area_id)
            except: pass
            
        member.save() 

        f_names = request.POST.getlist('member_name[]')
        f_phones = request.POST.getlist('member_phone[]')
        f_dobs = request.POST.getlist('member_dob[]')
        f_status = request.POST.getlist('member_married[]')
        f_spouses = request.POST.getlist('member_spouse_name[]')
        f_spouse_phones = request.POST.getlist('member_spouse_phone[]')
        f_spouse_dobs = request.POST.getlist('member_spouse_dob[]')

        member.family_members.all().delete()

        for i in range(len(f_names)):
            name_val = f_names[i].strip()
            if name_val:
                FamilyMember.objects.create(
                    member=member,
                    name=name_val,
                    phone=f_phones[i] if i < len(f_phones) else "",
                    dob=f_dobs[i] if (i < len(f_dobs) and f_dobs[i]) else None,
                    marital_status=f_status[i] if i < len(f_status) else "unmarried",
                    spouse_name=f_spouses[i] if i < len(f_spouses) else "",
                    spouse_phone=f_spouse_phones[i] if i < len(f_spouse_phones) else "",
                    spouse_dob=f_spouse_dobs[i] if (i < len(f_spouse_dobs) and f_spouse_dobs[i]) else None
                )
                print(f"DEBUG: Updated and Saved family member {name_val}")

        return redirect('profile_view', member_id=member.id)
def save_member(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        dob = request.POST.get('dob') or None
        marital_status = request.POST.get('marital_status')
        
        spouse_name = request.POST.get('spouse_name')
        spouse_phone = request.POST.get('spouse_phone')
        spouse_dob = request.POST.get('spouse_dob') or None
        
        gotra = request.POST.get('gotra')
        detailed_address = request.POST.get('detailed_address')
        pin = request.POST.get('pin')
        
        area_id = request.POST.get('area')
        area_obj = None
        if area_id:
            area_obj = Area.objects.get(id=area_id)

        member = Member.objects.create(
            name=name,
            phone_number=phone_number,
            dob=dob,
            marital_status=marital_status,
            spouse_name=spouse_name,
            spouse_phone=spouse_phone,
            spouse_dob=spouse_dob,
            gotra=gotra,
            detailed_address=detailed_address,
            pin=pin,
            area=area_obj,
            is_head=True  
        )

        f_names = request.POST.getlist('member_name[]')
        f_phones = request.POST.getlist('member_phone[]')
        f_dobs = request.POST.getlist('member_dob[]')
        f_status = request.POST.getlist('member_married[]')
        f_sp_names = request.POST.getlist('member_spouse_name[]')
        f_sp_phones = request.POST.getlist('member_spouse_phone[]')
        f_sp_dobs = request.POST.getlist('member_spouse_dob[]')

        for i in range(len(f_names)):
            name_val = f_names[i].strip()
            if name_val:
                FamilyMember.objects.create(
                    member=member,
                    name=name_val,
                    phone=f_phones[i] if i < len(f_phones) else "",
                    dob=f_dobs[i] if (i < len(f_dobs) and f_dobs[i]) else None,
                    marital_status=f_status[i] if i < len(f_status) else "unmarried",
                    spouse_name=f_sp_names[i] if i < len(f_sp_names) else "",
                    spouse_phone=f_sp_phones[i] if i < len(f_sp_phones) else "",
                    spouse_dob=f_sp_dobs[i] if (i < len(f_sp_dobs) and f_sp_dobs[i]) else None
                )

        return redirect('profile_view', member_id=member.id)
    
    return redirect('register') 


def edit_profile(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    areas = Area.objects.all()

    if request.method == "POST":
        member.name = request.POST.get('name')
        member.phone_number = request.POST.get('phone_number')
        member.pin = request.POST.get('pin')
        member.dob = request.POST.get('dob') or None
        member.marital_status = request.POST.get('marital_status')
        
        member.spouse_name = request.POST.get('spouse_name')
        member.spouse_phone = request.POST.get('spouse_phone')
        member.spouse_dob = request.POST.get('spouse_dob') or None
        
        member.gotra = request.POST.get('gotra')
        member.detailed_address = request.POST.get('detailed_address')
        
        area_id = request.POST.get('area')
        if area_id:
            try:
                member.area = Area.objects.get(id=area_id)
            except: pass

        member.is_head = True 
        
        member.save()

        # 3. Family Members Logic (Dynamic lists)
        f_names = request.POST.getlist('member_name[]')
        f_phones = request.POST.getlist('member_phone[]')
        f_dobs = request.POST.getlist('member_dob[]')
        f_status = request.POST.getlist('member_married[]')
        f_sp_names = request.POST.getlist('member_spouse_name[]')
        f_sp_phones = request.POST.getlist('member_spouse_phone[]') 
        f_sp_dobs = request.POST.getlist('member_spouse_dob[]')     

        member.family_members.all().delete()
        
        for i in range(len(f_names)):
            name_val = f_names[i].strip()
            if name_val:  
                FamilyMember.objects.create(
                    member=member,
                    name=name_val,
                    phone=f_phones[i] if i < len(f_phones) else "",
                    dob=f_dobs[i] if (i < len(f_dobs) and f_dobs[i]) else None,
                    marital_status=f_status[i] if i < len(f_status) else "unmarried",
                    spouse_name=f_sp_names[i] if i < len(f_sp_names) else "",
                    spouse_phone=f_sp_phones[i] if i < len(f_sp_phones) else "",
                    spouse_dob=f_sp_dobs[i] if (i < len(f_sp_dobs) and f_sp_dobs[i]) else None
                )

        return redirect('profile_view', member_id=member.id)

    return render(request, 'register.html', {
        'member': member, 
        'areas': areas, 
        'edit_mode': True,
        'temp_phone': member.phone_number
    })
def directory_view(request):
    query = request.GET.get('search', '') 
    
    if query:
        members = Member.objects.filter(
            Q(name__icontains=query) | Q(phone_number__icontains=query)
        ).order_by('name')
    else:
        members = Member.objects.all().order_by('name')

    return render(request, 'directory_list.html', {'members': members, 'query': query})

def profile_view(request, member_id):
    from django.shortcuts import get_object_or_404
    member = get_object_or_404(Member, id=member_id)
    
    family_members = member.family_members.all()
    
    context = {
        'member': member,
        'family_members': family_members
    }
    return render(request, 'profile.html', context)
def home(request): 
    return render(request, 'home.html')