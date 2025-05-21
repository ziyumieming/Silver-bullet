const axios = require('axios');
const { app } = require('@azure/functions');

app.http('chatCompletion', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (req, context) => {
		
		context.log(`Http function processed request for url "${req.url}"`);

		const userInput = await req.json();
		// context.log(`UserInput is "${JSON.stringify(userInput, null, 2)}"`);
        const url = "https://maas-cn-east-4.modelarts-maas.com/v1/infers/ea879672-0544-4194-96c2-2b2a9f79f4b3/v1/chat/completions"; // API 地址
        const apiKey = Environment.GetEnvironmentVariable("HuaweiAPIKey");


        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
        };

        const data = {
            "model": "Qwen2.5-72B",  // 模型名称
            "messages": [
                { "role": "system", "content": "You are a assistant that is good at sarcasm and offensive tone. Use Chinese in conversations." },
                { "role": "user", "content": userInput.content }
            ],
            "stream": false,  // 是否开启流式推理
            "temperature": 0.6  // 控制采样随机性
        };
		context.log(`UserInput is "${JSON.stringify(data, null, 2)}"`);
		

        try {
            // 发送请求到 API
            const response = await axios.post(url, data, { headers });
			// context.log(`得到的结果是 "${JSON.stringify(response.data, null, 2)}"`);
			// context.log(`得到的结果2是 "${JSON.stringify(response.data.choices[0].message.content, null, 2)}"`);
            // 返回 API 的响应给请求方
            return {
    		body: response.data.choices[0].message.content // 返回的响应内容
		};
			
        } catch (error) {
            // 处理错误
            return {
    		body: error.message		
};

        }
    }
});
