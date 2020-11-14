
var Person = React.createClass({
	propTypes: {
	    sex: React.PropTypes.string.isRequired,
	    name: React.PropTypes.string.isRequired,
	    dates: React.PropTypes.string.isRequired,
	    isAlive: React.PropTypes.bool.isRequired
	},

	render: function() {
	    
	    var sexAbbr = this.props.sex === "M" ? "male" : "female";
	    var isAlive = this.props.isAlive;

	    var classNameTxt = sexAbbr;

	    if(!isAlive) { 
		classNameTxt += " deceased";
	    }
		
	    return(<li className={classNameTxt}>
		   <div>
		   <div className="info">
		   <div className="name">{this.props.name}</div>
		   <div className="dates">{this.props.dates}</div>
		   </div>
		   <div className="icon rightArrow"></div>
		   <div className="icon sex"></div>
		   <div className="icon rip"></div>
		   </div>
		   </li>);
	}
    }
);	

var List = React.createClass({
	propTypes: {
	    people: React.PropTypes.array
	},
	getDefaultProps: function() {
	    return {
		people: mock["data"]
	    };
	},
	render: function() {

	    var persons = this.props.people;

	    var personObjs = persons.map(function(person) {
		    return(<Person sex={person.sex} name={person.name} dates={person.years} isAlive={person.isAlive} />);
		});

	    return (<ul className="persons">{personObjs}</ul>);
	}
    });

ReactDOM.render(<List  />, document.getElementById('list-react'));
	    