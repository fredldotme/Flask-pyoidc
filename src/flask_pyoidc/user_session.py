import time


class UninitialisedSession(Exception):
    pass


class UserSession:
    """Session object for user login state.

    Wraps comparison of times necessary for session handling.
    """

    KEYS = ['access_token', 'current_provider', 'id_token', 'id_token_jwt', 'last_authenticated', 'userinfo']

    def __init__(self, session_storage, provider_name=None):
        self._session_storage = session_storage
        if 'current_provider' not in self._session_storage and not provider_name:
            raise UninitialisedSession("Trying to pick-up uninitialised session without specifying 'provider_name'")

        if provider_name:
            if 'current_provider' in self._session_storage and \
                    provider_name != self._session_storage['current_provider']:
                # provider has changed, initialise new session
                self.clear()

            self._session_storage['current_provider'] = provider_name

    def is_authenticated(self):
        """
        flask_session is empty when the session hasn't been initialised or has expired.
        Thus checking for existence of any item is enough to determine if we're authenticated.
        """

        return self._session_storage.get('last_authenticated') is not None

    def should_refresh(self, refresh_interval_seconds=None):
        current_time = time.time()
        token_exp = (self._session_storage.get('token_exp', 0) - 20)
        return current_time > token_exp

    def _refresh_time(self, refresh_interval_seconds):
        last = self._session_storage.get('last_authenticated', 0)
        return last + refresh_interval_seconds

    def update(self, access_token=None, id_token=None, id_token_jwt=None, userinfo=None):
        """
        Args:
            access_token (str)
            id_token (Mapping[str, str])
            id_token_jwt (str)
            userinfo (Mapping[str, str])
        """

        def set_if_defined(session_key, value):
            if value:
                self._session_storage[session_key] = value

        auth_time = int(time.time())
        exp_time = int(time.time() + 300)
        if id_token:
            auth_time = id_token.get('auth_time', auth_time)
            exp_time = id_token.get('exp', exp_time)

        self._session_storage['last_authenticated'] = auth_time
        self._session_storage['token_exp'] = exp_time
        set_if_defined('access_token', access_token)
        set_if_defined('id_token', id_token)
        set_if_defined('id_token_jwt', id_token_jwt)
        set_if_defined('userinfo', userinfo)

    def clear(self):
        for key in self.KEYS:
            self._session_storage.pop(key, None)

    @property
    def access_token(self):
        return self._session_storage.get('access_token')

    @property
    def id_token(self):
        return self._session_storage.get('id_token')

    @property
    def id_token_jwt(self):
        return self._session_storage.get('id_token_jwt')

    @property
    def userinfo(self):
        return self._session_storage.get('userinfo')

    @property
    def current_provider(self):
        return self._session_storage.get('current_provider')

    @property
    def last_authenticated(self):
        return self._session_storage.get('last_authenticated')
