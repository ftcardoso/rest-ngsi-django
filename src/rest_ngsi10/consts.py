from django.conf import settings

FULLY_COMPATIBLE_SERIALIZER = getattr(settings, 'FULLY_COMPATIBLE_SERIALIZER', True)

if FULLY_COMPATIBLE_SERIALIZER:
    ELEMENT_KEY = 'contextElement'
    STATUS_KEY = 'statusCode'
    REASON_KEY = 'reasonPhrase'
    ERROR_KEY = 'errorCode'
    RESPONSES_KEY = 'contextResponses'
else:
    ELEMENT_KEY = 'element'
    STATUS_KEY = 'code'
    REASON_KEY = 'phrase'
    ERROR_KEY = 'error'
    RESPONSES_KEY = 'responses'
