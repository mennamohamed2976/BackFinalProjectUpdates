from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client
import os

class SupabaseStorage(Storage):
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = 'stods-files'

    def _save(self, name, content):
        self.client.storage.from_(self.bucket).upload(
            name, content.read(), {"content-type": content.content_type or "application/octet-stream"}
        )
        return name

    def url(self, name):
        return self.client.storage.from_(self.bucket).get_public_url(name)

    def exists(self, name):
        return False

    def delete(self, name):
        self.client.storage.from_(self.bucket).remove([name])
