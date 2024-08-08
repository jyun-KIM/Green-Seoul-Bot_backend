from flask_restx import fields

def define_models(chatbot_namespace):
    # DB에 사용하진 않지만 Swagger에 표기를 위한 model 작성
    image_upload_model = chatbot_namespace.model('ImageUpload', {
        'image_file': fields.String(required=True, description='사진 업로드 모델')
    })

    policy_info_model = chatbot_namespace.model('PolicyInfo', {
        'district_name': fields.String(required=True, description='정책정보 모델')
    })

    user_input_model = chatbot_namespace.model('UserInput', {
        'user_input': fields.String(required=True, description='유저 인풋 텍스트')
    })

    return image_upload_model, policy_info_model, user_input_model