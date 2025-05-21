
const { app } = require('@azure/functions');

app.http('test', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (req, context) => {
		
		context.log(`Http function processed request for url "${req.url}"`);
		const bod = await req.json();
		const userInput = bod || await req.text()
		// context.log(`UserInput is "${JSON.stringify(bod.content, null, 2)}"`);
		const answer =JSON.stringify(bod.content, null, 2)
		return{body:answer}
    }
});
