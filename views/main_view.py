from flask import Blueprint, Flask, jsonify, request, render_template
from openai import OpenAI, ChatCompletion

bp = Blueprint('main', __name__, url_prefix='/')

# gpt api
@bp.route('/ask', methods=['GET', 'POST']) 
def get_response():
    if request.method == 'POST':  
        user_question = request.form['question'] 

        client = OpenAI(
            api_key=''
            )

        # ChatGPT API 호출
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "당신은 폐기물 분리 AI챗봇입니다. '안녕하세요. 폐기물 분리 AI챗봇입니다. 무엇을 도와드릴까요?'로 시작해줘."},
                {"role": "user", "content": user_question},
                {"role": "assistant", "content": """
                    종이팩은 내용물을 비우고 물로 한번 헹군 후 펼치거나 압착하여 봉투에 넣거나 한데 묶어서 버립니다.
             음료수병, 기타 병류는 병뚜껑을 제거한 후 내용물을 비우고 배출합니다. 병 안에 담배꽁초 등 이물질을 제거해야 합니다.
             철캔과 알루미늄캔은 내용물을 비우고 가능한 압착 합니다. 겉에 있는 플라스틱 뚜껑을 제거해야 합니다. 병 안에 담배꽁초 등 이물질을 제거해야 합니다.
             기타 캔류(부탄가스, 살충제 용기)는 굼어을 뚫어 내용물을 비운 후 배출합니다.
             PET, PVC, PE, PP, PS, PSP 재질의 용기는 내용물을 깨끗이 비우고 다른 재질로 된 뚜껑이나 부착상표를 제거하고 가능한 압착해서 배출합니다.
             스티로폼 완충재는 TV, 냉장고, 세탁기, 에어컨, PC 제품의 발포합성수지 완충재는 제품 구입처로 반납합니다.
             스티로폼 완충재는 내용물을 완전히 비우고 부착상표를 제거하고, 이물질을 씻어서 배출합니다.
             신문지는 물기에 젖지 않도록 반듯하게 펴서 차곡차곡 쌓은 후 묶어서 배출합니다.
             노트, 책자는 비닐 코팅된 표지와 스프링은 제거합니다.
             종이컵은 내용물을 비우고 물로 헹군 후 압착하여 봉투에 넣습니다.
             골판지 상자, 상자는 비닐 코팅 부분, 상자에 붙어있는 테이프, 철핀 등을 제거한 후 압착하여 운반이 용이하도록 묶어서 배출합니다.
             소형 가전제품은 재활용 하는 날 다른 재활용품과 함께 배출하거나 전용 수거용기에 배출합니다.
             TV, 세탁기, 냉장고, 에어컨은 신고 후 배출합니다.
             고철(공기구, 철사, 못)과 비철금속(알루미늄, 스텐)은 이물질이 섞이지 않도록 한 후 봉투에 넣거나 끈으로 묶어서 배출합니다.
             의류는 물기에 젖지 않도록 마대 등에 담거나 묶어서 배출합니다.
             농약용기는 내용물을 완전히 사용한 후 유리병, 플라스틱 용기별로 구분하여 뚜껑을 분리, 마대 등에 따로 넣어 배출합니다.
             농촌폐비닐은 하우스용 비닐과 멀칭용 비닐을 구분하여 흙과 자갈, 잡초를 털어낸 후 운반이 쉽도록 묶어서 마을공동집하장 또는 수거, 운반차량 진입이 가능한 일정 장소에 보관합니다.
             가정용 플라스틱류, 1회용 비닐봉투, 이불류, 신발, 가방류, 전선관, 파이프, 호스, 장판류, 카페트, 폐식용유는 각 구에서 정해진 요령대로 배출해야하니 구청 사이트에서 확인하시기 바랍니다.
                 """}
            ]
        )
        # 질문과 답 반환
        response = chat_completion.choices[0].message.content
        return jsonify({"response": response}) # JSON 으로 반환

if __name__ == '__main__':
    app.run()



'''
# 회원가입
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

# 로그인


# 로그아웃
@bp.route('/logout')
def logout():

# ChatGPT API -- 폐기물 분리 봇
@bp.route('/gpt')
def gptapi():
    # OpenAI 응답 가져옴
    response = get_response()
    return render_template('index.html', response=response)
'''
