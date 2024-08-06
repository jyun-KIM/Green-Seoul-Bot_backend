from flask_restx import fields, Model

def create_chat_model(api):
    chat_model = api.model('Chat', {
        'user_input': fields.String(
            required=False,
            description='유저가 챗봇에 인풋'
        ),
        'payload': fields.String(
            required=True,
            description='Payload 요청 유형',
            enum=[
                "usage",
                "policy",
                "select_district",
                "input_district",
                "how_to_dispose",
                "upload_photo",
                "upload_another"
            ]
        ),
        'photo': fields.String(
            required=False,
            description='사진 업로드 실패'
        )
    })
    return chat_model

def create_chat_response_model(api):
    chat_response_model = api.model('ChatResponse', {
        'message': fields.String(
            required=True,
            description='Response'
        ),
        'buttons': fields.List(
            fields.Nested(api.model('Button', {
                'title': fields.String(
                    required=True,
                    description='Button title'
                ),
                'payload': fields.String(
                    required=False,
                    description='Button payload'
                ),
                'url': fields.String(
                    required=False,
                    description='Button URL'
                )
            }))
        )
    })
    return chat_response_model