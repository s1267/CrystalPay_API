import requests
import hashlib


class AuthorizationError(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


class OperationError(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


class CrystalPay:
    default_url = 'https://api.crystalpay.ru/v1/'

    def __init__(self, name, secret1, secret2):
        self.secret1 = secret1
        self.secret2 = secret2
        self.name = name

    def get_params(self, **kwargs):
        params = {
            's': self.secret1,
            'n': self.name,
        }
        params.update(kwargs)
        return params

    @staticmethod
    def _request(method, url, params):
        response = requests.request(method=method, url=url, params=params)
        auth_status = response.json()['auth']
        error_status = response.json()['error']
        if response.status_code == 200:
            if auth_status == 'ok':
                if error_status is True:
                    raise OperationError(response.json()['error_message'], 'operation_error')
                else:
                    return response.json()
            elif auth_status == 'error':
                raise AuthorizationError('Check SECRET1, SECRET2 and name cash register', 'auth_error')
            return response.json()
        else:
            raise requests.exceptions.RequestException

    @staticmethod
    def _create_secret_hash(*args):
        return hashlib.md5('@'.join([str(elem) for elem in args]).encode()).hexdigest()

    def create_receipt(self, amount, lifetime, extra=None, callback=None, redirect=None, currency=None):
        url = self.default_url
        operation = 'receipt-create'
        params = self.get_params(o=operation, amount=amount, lifetime=lifetime, extra=extra or None,
                                 callback=callback or None, redirect=redirect or None)
        if currency:
            r = self._request('GET', url, params)
            r['url'] = r['url'] + '&m=' + currency
            return r
        else:
            return self._request('GET', url, params)

    def check_receipt(self, receipt_id):
        url = self.default_url
        operation = 'receipt-check'
        params = self.get_params(o=operation, i=receipt_id)
        return self._request('GET', url, params)

    def get_balance(self):
        url = self.default_url
        operation = 'balance'
        params = self.get_params(o=operation)
        return self._request('GET', url, params)

    def create_withdraw(self, amount, currency, wallet, callback=None):
        url = self.default_url
        operation = 'withdraw'
        withdraw_secret = self._create_secret_hash(wallet, amount, self.secret2)
        params = self.get_params(o=operation, secret=withdraw_secret, amount=amount, wallet=wallet, currency=currency,
                                 callback=callback or None)
        return self._request('GET', url, params)

    def check_withdraw(self, withdraw_id):
        url = self.default_url
        operation = 'withdraw-status'
        params = self.get_params(o=operation, i=withdraw_id)
        return self._request('GET', url, params)

    def p2p_transfer(self, login, amount, currency):
        url = self.default_url
        operation = 'p2p-transfer'
        p2p_secret = self._create_secret_hash(currency, amount, login, self.secret2)
        params = self.get_params(o=operation, secret=p2p_secret, login=login, amount=amount, currency=currency)
        return self._request('GET', url, params)

    def create_voucher(self, amount, currency, comment=None):
        url = self.default_url
        operation = 'voucher-create'
        voucher_secret = self._create_secret_hash(currency, amount, self.secret2)
        if comment:
            params = self.get_params(o=operation, secret=voucher_secret, comment=comment)
        else:
            params = self.get_params(o=operation, secret=voucher_secret)
        return self._request('GET', url, params)

    def voucher_info(self, voucher_code):
        url = self.default_url
        operation = 'voucher-info'
        params = self.get_params(o=operation, code=voucher_code)
        return self._request('GET', url, params)

    def activate_voucher(self, voucher_code):
        url = self.default_url
        operation = 'voucher-activate'
        params = self.get_params(o=operation, code=voucher_code)
        return self._request('GET', url, params)

