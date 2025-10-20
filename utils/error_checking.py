




def get_error_status(response):
    """
    Checks the response for common status codes and error messages in the text.
    Returns a descriptive error message or "ok".
    """
    special_status_codes = {
        404: "not_found",
        403: "access_denied/Forbidden",
        402: "store_unavailable",
    }

    special_errors = {
        "sorry, this store is currently unavailable.": "store_unavailable",
        "this domain has expired": "domain_expired",
        "your connection is not private": "ssl_error",
        "this site can't be reached": "site_unreachable",
        "something went wrong": "page not found",
        "ups! irgendwas ist schief gelaufen": "generic_error_de",
        "lo sentimos, actualmente esta tienda no está disponible": "store_unavailable_es",
        "this store does not exist": "store_not_exist",
        "tut uns leid, dieser shop ist derzeit nicht verfügbar.": "store_unavailable_de",
        "we moved!": "site_moved",
        "STATUS_404":"something went wrong",
        "malheureusement, cette boutique n’est pas disponible actuellement.": "store_unavailable_fr",
        "this domain has expired. if you owned this name, contact your registration provider for assistance. to identify your provider, click here.": "domain_expired_notice"
    }
    # print(response.status_code)
    if response.status_code == 200:
        text_content = response.text.lower()
        for error, message in special_errors.items():
            if error.lower() in text_content:
                return message
        return "ok"
    else:
        if response.status_code in special_status_codes:
            return special_status_codes[response.status_code]
        else:
            return f"unknown_error_{response.status_code}"