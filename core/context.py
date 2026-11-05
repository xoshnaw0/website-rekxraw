from .models import SiteStats
def stats(request): return {"stats": SiteStats.get()}
