import re
import base64

from requests import Session

# Modified code based on DashLt's spoofbuz
_INFO_EXTRAS_REGEX = r'name:"\w+/(?P<timezone>{timezones})",info:"(?P<info>[\w=]+)",extras:"(?P<extras>[\w=]+)"'
_BASE_URL = "https://play.qobuz.com"
_BUNDLE_URL_REGEX = re.compile(
    r'<script src="(/resources/\d+\.\d+\.\d+-[a-z]\d{3}/bundle\.js)"></script>'
)
_SEED_TIMEZONE_REGEX = re.compile(
    r'[a-z]\.initialSeed\("(?P<seed>[\w=]+)",window\.utimezone\.(?P<timezone>[a-z]+)\)'
)
_APP_ID_REGEX_NEW = re.compile(
    r'production:{api:{appId:"(\d+)",appSecret:"\w+"}'
)


class Bundle:
    def __init__(self):
        self._session = Session()
        response = self._session.get(f"{_BASE_URL}/login")
        response.raise_for_status()

        bundle_url_match = _BUNDLE_URL_REGEX.search(response.text)
        if not bundle_url_match:
            raise NotImplementedError("Bundle URL found")

        bundle_url = bundle_url_match.group(1)

        response = self._session.get(_BASE_URL + bundle_url)
        response.raise_for_status()
        self._bundle = response.text

    def get_app_id(self):
        match = _APP_ID_REGEX_NEW.search(self._bundle)
        if not match:
            raise NotImplementedError("Failed to match APP ID")
        
        return match.group(1)

    def get_secret(self):
        seed_matches = _SEED_TIMEZONE_REGEX.finditer(self._bundle)

        for match in seed_matches:
            seed, timezone = match.group("seed", "timezone")
            if timezone == 'berlin':
                break

        info_extras_regex = _INFO_EXTRAS_REGEX.format(
            timezones="|".join([timezone.capitalize()])
        )
        info_extras_matches = re.finditer(info_extras_regex, self._bundle)
        for match in info_extras_matches:
            timezone, info, extras = match.group("timezone", "info", "extras")
            break

        secret = seed + info + extras
        secret = base64.standard_b64decode(
                secret[:-44]
            ).decode("utf-8")

        return secret
