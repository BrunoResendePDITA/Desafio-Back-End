from fastapi import HTTPException


def erro(status_code: int, mensagem: str):
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": mensagem,
            "statusCode": status_code
        }
    )
