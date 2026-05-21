
from urllib import request
import traceback
from django.shortcuts import render, redirect, get_object_or_404
from .models import Area, Member, FamilyMember
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
def smart_login(request):
    if request.method == "POST":
        print(f"🚨 TOTAL FORM DATA RECEIVED = {dict(request.POST)}")
        
        phone = request.POST.get('phone_number') or request.POST.get('phone') or ''
        phone = phone.strip()
        
        print(f"👉 DEBUG 1: Input Phone from Form = '{phone}'")

        clean_phone = ''.join(filter(str.isdigit, phone))
        if len(clean_phone) >= 10:
            clean_phone = clean_phone[-10:]
            
        print(f"👉 DEBUG 2: Cleaned 10-Digit Phone = '{clean_phone}'")

        if clean_phone:
            member = Member.objects.filter(phone_number__contains=clean_phone).first() or \
                     Member.objects.filter(login_number__contains=clean_phone).first()
            
            print(f"👉 DEBUG 3: Database Query Result = {member}")
            if member:
                print(f"👉 DEBUG 4: Matching Member Found! ID: {member.id}, Name: {member.name}")
                return redirect('profile_view', member_id=member.id)
            
            all_members = Member.objects.all()
            for m in all_members:
                db_phone = ''.join(filter(str.isdigit, m.phone_number or ''))
                db_login = ''.join(filter(str.isdigit, m.login_number or ''))
                
                if clean_phone in db_phone or clean_phone in db_login:
                    print(f"🎯 BACKUP MATCH FOUND! ID: {m.id}, Name: {m.name}")
                    return redirect('profile_view', member_id=m.id)
            
        return redirect(f'/register/?phone={clean_phone}')
            
    return render(request, 'home.html')


def register(request):
    try:
        areas = Area.objects.all()
        temp_phone = request.GET.get('phone', '')
        
        return render(request, 'register.html', {'areas': areas, 'temp_phone': temp_phone})
    except Exception as e:
        return HttpResponse(f"Register View Crashed: {str(e)}<br><pre>{traceback.format_exc()}</pre>", status=500)
def update_member(request, id=None, member_id=None):
    print("🔴 ALERT: update_member function chal raha hai!")
    target_id = id or member_id
    
    member = get_object_or_404(Member, id=target_id)
    
    if request.method == "POST":
        try:
            member.name = request.POST.get('name')
            
            # Phone cleaning logic
            phone = request.POST.get('phone_number', '').strip()
            clean_phone = ''.join(filter(str.isdigit, phone))
            if len(clean_phone) >= 10:
                clean_phone = clean_phone[-10:]
            
            if clean_phone:
                duplicate_exists = Member.objects.filter(phone_number=clean_phone).exclude(id=target_id).exists() or \
                                   Member.objects.filter(login_number=clean_phone).exclude(id=target_id).exists()
                if duplicate_exists:
                    return HttpResponse(f"<h2>Update Error:</h2><p>This phone number ({clean_phone}) is already registered with another member!</p>", status=400)
            
            member.phone_number = clean_phone
            member.login_number = clean_phone
            
            dob_val = request.POST.get('dob')
            member.dob = dob_val if (dob_val and dob_val.strip() != "") else None
            
            member.marital_status = request.POST.get('marital_status')
            member.gotra = request.POST.get('gotra')
            member.detailed_address = request.POST.get('detailed_address')
            member.pin = request.POST.get('pin')

            member.head_occupation = request.POST.get('head_occupation', '').strip()
            member.spouse_occupation = request.POST.get('spouse_occupation', '').strip()
            member.spouse_name = request.POST.get('spouse_name')
            member.spouse_phone = request.POST.get('spouse_phone')
            
            spouse_dob_val = request.POST.get('spouse_dob')
            member.spouse_dob = spouse_dob_val if (spouse_dob_val and spouse_dob_val.strip() != "") else None
            
            area_id = request.POST.get('area')
            if area_id:
                try:
                    member.area = Area.objects.get(id=area_id)
                except: 
                    pass
                
            member.save() 

            f_names = request.POST.getlist('member_name[]')
            f_phones = request.POST.getlist('member_phone[]')
            f_dobs = request.POST.getlist('member_dob[]')
            f_status = request.POST.getlist('member_married[]')
            f_sp_names = request.POST.getlist('member_spouse_name[]')
            f_sp_phones = request.POST.getlist('member_spouse_phone[]')
            f_sp_dobs = request.POST.getlist('member_spouse_dob[]')
            f_occupations = request.POST.getlist('member_occupation[]')

            FamilyMember.objects.filter(member=member).delete()

            for i in range(len(f_names)):
                name_val = f_names[i].strip()
                if name_val:
                    # 🌟 SAFE CLEANING: `.strip()` tabhi chalega jab string confirm ho
                    f_dob_val = f_dobs[i] if (i < len(f_dobs) and f_dobs[i] and str(f_dobs[i]).strip() != "") else None
                    f_sp_dob_val = f_sp_dobs[i] if (i < len(f_sp_dobs) and f_sp_dobs[i] and str(f_sp_dobs[i]).strip() != "") else None

                    occ_val = f_occupations[i].strip() if (i < len(f_occupations) and f_occupations[i]) else ""

                    FamilyMember.objects.create(
                        member=member,
                        name=name_val,
                        phone=f_phones[i] if i < len(f_phones) else "",
                        dob=f_dob_val,
                        marital_status=f_status[i] if i < len(f_status) else "unmarried",
                        spouse_name=f_sp_names[i] if i < len(f_sp_names) else "",
                        spouse_phone=f_sp_phones[i] if i < len(f_sp_phones) else "",
                        spouse_dob=f_sp_dob_val,
                        occupation=occ_val
                    )
            
            return redirect('profile_view', member_id=member.id)

        except Exception as e:
            import traceback
            print("🔴🔴 UPDATE FUNCTION CRASHED 🔴🔴")
            print(traceback.format_exc())
            return HttpResponse(f"<h2>Update Error Detailing:</h2><pre>{traceback.format_exc()}</pre>", status=500)
            
    return redirect('profile_view', member_id=member.id)
def save_member(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            phone_number = request.POST.get('phone_number')
            phone = request.POST.get('phone_number', '').strip()
            phone_number = ''.join(filter(str.isdigit, phone))
            if len(phone_number) >= 10:
                phone_number = phone_number[-10:]
            dob = request.POST.get('dob')
            if not dob or dob.strip() == "":
                dob = None
                
            marital_status = request.POST.get('marital_status')
            spouse_name = request.POST.get('spouse_name')
            spouse_phone = request.POST.get('spouse_phone')
            
            spouse_dob = request.POST.get('spouse_dob')
            if not spouse_dob or spouse_dob.strip() == "":
                spouse_dob = None
            
            head_occupation_val = request.POST.get('head_occupation') or ""
            spouse_occupation_val = request.POST.get('spouse_occupation') or ""
            
            gotra = request.POST.get('gotra')
            detailed_address = request.POST.get('detailed_address')
            pin = request.POST.get('pin')
            
            area_id = request.POST.get('area')
            area_obj = None
            if area_id and area_id.strip() != "":
                area_obj = Area.objects.get(id=area_id)

            # Mukhiya create kar rahe hain
            member = Member.objects.create(
                name=name,
                phone_number=phone_number,
                login_number=phone_number,
                dob=dob,
                marital_status=marital_status,
                spouse_name=spouse_name,
                spouse_phone=spouse_phone,
                spouse_dob=spouse_dob,
                head_occupation=head_occupation_val,  
                spouse_occupation=spouse_occupation_val, 
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
            f_occupations = request.POST.getlist('member_occupation[]')
            f_spouse_occupations = request.POST.getlist('member_spouse_occupation[]')

            for i in range(len(f_names)):
                name_val = f_names[i].strip()
                if name_val:
                    f_dob_val = f_dobs[i] if (i < len(f_dobs) and f_dobs[i].strip() != "") else None
                    f_sp_dob_val = f_sp_dobs[i] if (i < len(f_sp_dobs) and f_sp_dobs[i].strip() != "") else None
                    occ_val = f_occupations[i].strip() if (i < len(f_occupations) and f_occupations[i]) else ""
                    sp_occ_val = ""
                    if i < len(f_spouse_occupations) and f_spouse_occupations[i]:
                         sp_occ_val = f_spouse_occupations[i].strip()
                    FamilyMember.objects.create(
                        member=member,
                        name=name_val,
                        phone=f_phones[i] if i < len(f_phones) else "",
                        dob=f_dob_val,
                        marital_status=f_status[i] if i < len(f_status) else "unmarried",
                        spouse_name=f_sp_names[i] if i < len(f_sp_names) else "",
                        spouse_phone=f_sp_phones[i] if i < len(f_sp_phones) else "",
                        spouse_dob=f_sp_dob_val,
                        occupation=occ_val,
                        spouse_occupation=sp_occ_val
                    )

            return redirect('profile_view', member_id=member.id)
            
        except Exception as e:
            import traceback
            print("🔴🔴 BHYANKAR BACKEND ERROR DETECTED 🔴🔴")
            print(traceback.format_exc())
            from django.http import HttpResponse
            return HttpResponse(f"Backend Crashed: {str(e)}<br><pre>{traceback.format_exc()}</pre>", status=500)
    
    return redirect('register')
def edit_profile(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    areas = Area.objects.all()

    if request.method == "POST":
        # 1. Basic Fields update
        member.name = request.POST.get('name')
        member.phone_number = request.POST.get('phone_number')
        member.pin = request.POST.get('pin')
        member.dob = request.POST.get('dob') or None
        member.marital_status = request.POST.get('marital_status')
        member.gotra = request.POST.get('gotra')
        member.detailed_address = request.POST.get('detailed_address')
        
        # 2. Occupation Fields (Naye fields yahan catch honge)
        member.head_occupation = request.POST.get('head_occupation', '').strip()
        member.spouse_occupation = request.POST.get('spouse_occupation', '').strip()
        
        # Spouse fields
        member.spouse_name = request.POST.get('spouse_name')
        member.spouse_phone = request.POST.get('spouse_phone')
        member.spouse_dob = request.POST.get('spouse_dob') or None
        
        # Area update
        area_id = request.POST.get('area')
        if area_id:
            try:
                member.area = Area.objects.get(id=area_id)
            except: pass

        member.save()
        print("✅ SUCCESS: edit_profile view hit ho gaya!") 

        # 3. Family Members Logic
        member.family_members.all().delete()
        f_names = request.POST.getlist('member_name[]')
        f_phones = request.POST.getlist('member_phone[]')
        f_dobs = request.POST.getlist('member_dob[]')
        f_status = request.POST.getlist('member_married[]') 
        f_sp_names = request.POST.getlist('member_spouse_name[]')
        f_sp_phones = request.POST.getlist('member_spouse_phone[]')
        f_sp_dobs = request.POST.getlist('member_spouse_dob[]')
        f_occupations = request.POST.getlist('member_occupation[]')
        f_spouse_occupations = request.POST.getlist('member_spouse_occupation[]')
        sp_idx = 0
        for i in range(len(f_names)):
            if f_names[i].strip():
                sp_occ = ""
                if f_status[i] == 'married' and sp_idx < len(f_spouse_occupations):
                    sp_occ = f_spouse_occupations[sp_idx].strip()
                    sp_idx += 1 
                
                FamilyMember.objects.create(
                    member=member,
                    name=f_names[i].strip(),
                    phone=f_phones[i] if i < len(f_phones) else "",
                    dob=f_dobs[i] if (i < len(f_dobs) and f_dobs[i].strip()) else None,
                    marital_status=f_status[i] if i < len(f_status) else "unmarried",
                    spouse_name=f_sp_names[i] if i < len(f_sp_names) else "",
                    spouse_phone=f_sp_phones[i] if i < len(f_sp_phones) else "",
                    spouse_dob=f_sp_dobs[i] if (i < len(f_sp_dobs) and f_sp_dobs[i].strip()) else None,
                    occupation=f_occupations[i].strip() if i < len(f_occupations) else "",
                    spouse_occupation=sp_occ
                )
        return redirect('profile_view', member_id=member.id)

    return render(request, 'register.html', {
        'member': member, 
        'areas': areas, 
        'edit_mode': True
    })

def directory_view(request):
    query = request.GET.get('search', '') 
    
    if query:
        members = Member.objects.filter(
            Q(name__icontains=query) | Q(phone_number__icontains=query)
        ).order_by('area__name', 'name')
    else:
        members = Member.objects.all().order_by('area__name', 'name')

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