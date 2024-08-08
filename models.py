from flask_restx import fields

def define_models(chatbot_namespace):
    # DB에 사용하진 않지만 Swagger에 표기를 위한 model 작성
    image_upload_model = chatbot_namespace.model('ImageUploadDTO', {
        'image_file': fields.String(required=True, description='사진 업로드')
    })

    policy_info_model = chatbot_namespace.model('PolicyInfoDTO', {
        'district_name': fields.String(required=True, description='정책정보')
    })

    user_input_model = chatbot_namespace.model('UserInputDTO', {
        'user_input': fields.String(required=True, description='유저 인풋 텍스트')
    })

    image_upload_response_model = chatbot_namespace.model('ImageUploadResponseDTO', {
        'message': fields.String(description='Response message')
    })

    policy_info_response_model = chatbot_namespace.model('PolicyInfoResponseDTO', {
        'message': fields.String(description='Response message from ChatGPT'),
        'homepage_url': fields.String(description='URL of the district homepage')
    })

    chat_response_model = chatbot_namespace.model('ChatResponseDTO', {
        'message': fields.String(description='Response message from ChatGPT')
    })

    return image_upload_model, policy_info_model, user_input_model, image_upload_response_model, policy_info_response_model, chat_response_model