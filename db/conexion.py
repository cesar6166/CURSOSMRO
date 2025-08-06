from supabase import create_client, Client

# Credenciales
SUPABASE_URL = "https://iawgsobarfbbcutjqetu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlhd2dzb2JhcmZiYmN1dGpxZXR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0OTgyNTksImV4cCI6MjA3MDA3NDI1OX0.CP1EW34hbLX93Y_20tEKaUCWo_8W4E847G7RrgcB8i4"

def get_connection() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
