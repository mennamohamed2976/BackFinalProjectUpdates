import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orgen.models import User
from orgen.ai_matching import trigger_ai_matching

donors = User.objects.filter(role='donor')
print(f"Doner Number : {donors.count()}")

for donor in donors:
    print(f"\n🔄 Loading donor: {donor.first_name} {donor.last_name}")
    result = trigger_ai_matching(donor)
    if result:
        print(f"✅ Success! Number of matches: {len(result.get('top_matches', []))}")
    else:
        print("❌ Failed or no matching patients for this organ")

from orgen.models import OrganMatching
print(f"\n🎉 Total matches in the database: {OrganMatching.objects.count()}")