
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
};

const apiSingleton = new API();

export default apiSingleton;