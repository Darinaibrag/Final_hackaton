from datetime import datetime

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from config.celery import app



@app.task(bind=True)
def clear_tokens(self):
    BlacklistedToken.objects.filter(token__expires_at__lt=datetime.now()).delete()
    OutstandingToken.objects.filter(expires_at__lt=datetime.now()).delete()
    return 'Deleted expired tokens'
