from django.db import models
from datetime import date
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

class Area(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Member(models.Model):
    login_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    pin = models.CharField(max_length=4, default="0000")
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    gotra = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    
    # Marital Info
    marital_status = models.CharField(max_length=20, default='unmarried')
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_phone = models.CharField(max_length=15, blank=True, null=True)
    spouse_dob = models.DateField(null=True, blank=True)

    # Mukhiya Info
    is_head = models.BooleanField(default=True)
    head_name = models.CharField(max_length=100, blank=True, null=True)
    head_phone = models.CharField(max_length=15, blank=True, null=True)
    head_dob = models.DateField(blank=True, null=True)
    head_marital_status = models.CharField(max_length=20, blank=True, null=True)
    head_spouse_name = models.CharField(max_length=100, blank=True, null=True)
    head_spouse_phone = models.CharField(max_length=15, blank=True, null=True)
    head_spouse_dob = models.DateField(blank=True, null=True)

    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    detailed_address = models.TextField()

    registration_no = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.registration_no:
            last_member = Member.objects.order_by('-registration_no').first()
            if last_member and last_member.registration_no:
                self.registration_no = last_member.registration_no + 1
            else:
                self.registration_no = 1
        super().save(*args, **kwargs)


    @property
    def age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
    @property
    def head_age(self):
      if self.head_dob:
        today = date.today()
        return today.year - self.head_dob.year - ((today.month, today.day) < (self.head_dob.month, self.head_dob.day))
      return None

    @property
    def head_spouse_age(self):
        if self.head_spouse_dob:
            today = date.today()
            return today.year - self.head_spouse_dob.year - ((today.month, today.day) < (self.head_spouse_dob.month, self.head_spouse_dob.day))
        return None
@receiver(post_delete, sender=Member)
def reorder_registration_numbers(sender, instance, **kwargs):
    all_members = Member.objects.order_by('id') # ya 'registration_no'
    for index, member in enumerate(all_members, start=1):
        if member.registration_no != index:
            member.registration_no = index
            # Hum sirf registration_no update kar rahe hain bina baki database fields ko disturb kiye
            Member.objects.filter(id=member.id).update(registration_no=index)

class FamilyMember(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, default='unmarried')
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_phone = models.CharField(max_length=15, null=True, blank=True)
    spouse_dob = models.DateField(null=True, blank=True)

    @property
    def age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
    
    @property
    def spouse_age(self):
        if self.spouse_dob:
            today = date.today()
            return today.year - self.spouse_dob.year - ((today.month, today.day) < (self.spouse_dob.month, self.spouse_dob.day))
        return None