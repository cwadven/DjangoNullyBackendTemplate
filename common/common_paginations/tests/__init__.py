from common.common_criteria.cursor_criteria import CursorCriteria


class MockCursorCriteria(CursorCriteria):
    cursor_keys = ['id__lte']

    @classmethod
    def get_encoded_base64_cursor_data(cls, data):
        return f'cursor_for_{data.id}'
