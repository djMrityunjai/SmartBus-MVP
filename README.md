### Database Setup

1. Run the following commands:

python manage.py migrate --run-syncdb

python manage.py shell

```
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
quit()
```

python manage.py loaddata datadump.json
