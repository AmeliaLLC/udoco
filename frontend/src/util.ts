const TOKEN_NAME = 'csrftoken';

function getCSRFToken(): string {
    if (document.cookie && document.cookie !== '') {
        for (const cookie of document.cookie.split(';')) {
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, TOKEN_NAME.length + 1) === (TOKEN_NAME + '=')) {
                return decodeURIComponent(cookie.substring(TOKEN_NAME.length + 1));
                break;
            }
        }
    }
    return 'missing-csrftoken';
}

export { getCSRFToken };
