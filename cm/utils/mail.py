"""
Simple extension of django's EmailMessage to store emails in db
"""
from django.core.mail import EmailMessage as BaseEmailMessage
from cm.models import Email
 
LIST_SEP = ' '

class EmailMessage(BaseEmailMessage):
    
    def send(self, fail_silently=False):
        # store in db
        Email.objects.create(
                             from_email = self.from_email,
                             to = LIST_SEP.join(self.to),
                             bcc = LIST_SEP.join(self.bcc),
                             body = self.body,
                             subject = self.subject, 
                             )
        # then send for real
        BaseEmailMessage.send(self,fail_silently)
     