import {axios} from 'axios'

async function create_model(name,value) {
    
    var body = {
        name:name,
        value:value
    }
    var answer = await axios.post("/model1", body, {
        "Content-type": "application/json; charset=UTF-8"
    }
    );
    var text = answer["data"]
    if (answer.status == 200) {
        response.value = text["message"]
    }
    else if (answer.status == 400) {
        request.value = true
        alert(text["detail"])
    }
    else if (answer.status == 422) {
        request.value = true
        alert(JSON.stringify(text))
    }

}