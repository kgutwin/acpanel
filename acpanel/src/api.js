
class API {
    constructor() {
	this.changeNotifications = [];
	this.poll = this.poll.bind(this);
	setInterval(this.poll, 5000);
    }

    subscribe(onChange) {
	this.changeNotifications.push(onChange);
    }

    unsubscribe(onChange) {
	const index = this.changeNotifications.indexOf(onChange);
	if (index > -1) {
	    this.changeNotifications.splice(index, 1);
	}
    }

    poll() {
	if (this.changeNotifications.length === 0) return;

	fetch('/api/shadow')
	    .then(response => response.json())
	    .then(data => {
		    this.changeNotifications.forEach(func => {
			    func(data)
			});
		})
	    .catch((error) => { console.error('Error:', error); });
    }

    update(desired) {
	const opts = {
	    method: 'PUT',
	    headers: {'Content-Type': 'application/json'},
	    body: JSON.stringify({state: {desired}})
	};
	return fetch('/api/shadow', opts)
	    .then(response => response.json())
	    .then(data => {
		    this.changeNotifications.forEach(func => {func(data)});
		})
	    .catch((error) => { console.error('Update error:', error); });
    }

    isAuth() {
	return fetch('/api/auth').then(response => response.json())
	    .catch((error) => { console.error('Auth check error:', error); });
    }

    signin(accessKey) {
	const opts = {
	    method: 'POST',
	    headers: {
		'Content-Type': 'application/json'
	    },
	    body: JSON.stringify({ access_token: accessKey })
	};
	return fetch('/api/auth', opts)
	    .then(response => response.json())
	    .catch((error) => { console.error('Signin error:', error); });
    }
};

const apiSingleton = new API();

export default apiSingleton;