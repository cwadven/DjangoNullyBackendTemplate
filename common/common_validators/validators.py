class ValidationErrorContext(dict):
    def add_error(self, field: str, error: str):
        value = self.setdefault(field, [])
        value.append(error)


class PayloadValidator(object):
    def __init__(self, payload: dict):
        self.payload = payload
        self.error_context = ValidationErrorContext()
        self.skip_validate_keys = set()

    def add_error_context(self, key: str, description: str):
        """
        only add error if key is not in 'skip_validate_keys'
        """
        if not (key in self.skip_validate_keys):
            self.error_context.add_error(key, description)

    def add_error_and_skip_validation_key(self, key: str, description: str):
        """
        add only main error so other errors cannot add
        """
        self.add_error_context(key, description)
        self.skip_validate_keys.add(key)

    def _get_meta_attribute(self):
        return getattr(self, 'Meta', None)

    def _validate_payloads_type(self):
        """
        validate payload types from class Meta 'type_of_keys'
        if list of first index is type or tuple then use isinstance to check type else check as function
        if function it must return boolean
        list of second index is used for error message
        """
        meta = self._get_meta_attribute()
        if meta:
            for key, value in getattr(meta, 'type_of_keys', {}).iteritems():
                type_or_func, error_msg = value

                if isinstance(type_or_func, (type, tuple)):
                    if not isinstance(self.payload[key], type_or_func):
                        self.add_error_and_skip_validation_key(key, error_msg)
                elif not type_or_func(self.payload[key]):
                    self.add_error_and_skip_validation_key(key, error_msg)

    def common_validate(self):
        """
        first check mandatory keys then check key types
        """
        self._validate_payloads_type()
