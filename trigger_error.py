import os
import django
import sys
from django.test import RequestFactory

# Setup Django environment
sys.path.append(r'd:\VPS_Plat_Edwared_v01')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edwared_cloud.settings')
django.setup()

from apps.flores.views import home

def trigger_view():
    print("Simulating request to /flores/...")
    rf = RequestFactory()
    request = rf.get('/flores/')
    try:
        response = home(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code >= 500:
            print("Response Content:")
            print(response.content.decode('utf-8')[:1000])
    except Exception as e:
        import traceback
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()

if __name__ == '__main__':
    trigger_view()
