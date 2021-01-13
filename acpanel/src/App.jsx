import React, { useState, useEffect } from 'react';
import { 
  Button, Container, Header, Statistic, Label, Segment, Input, Checkbox,
  Progress, Grid
} from 'semantic-ui-react';
import './App.css';
import API from './api';


function AcStatus() {
  const [acState, setAcState] = useState({});

  useEffect(() => {
    function handleStatusChange(status) {
      setAcState(status);
    };
    API.subscribe(handleStatusChange);
    return function cleanup() {
      API.unsubscribe(handleStatusChange);
    };
  });

  console.log(acState);

  if ("state" in acState) {
    const firstRow = [
      { key: 'setTemp', label: 'Set Temp',
        value: acState.state.reported.current_set_t },
      { key: 'currentTemp', label: 'Current Temp',
        value: acState.state.reported.current_t.toFixed(1) },
    ];
    const secondRow = [
      { key: 'enabled', label: 'Enabled',
        value: acState.state.reported.enable ? "true" : "false",
        color: acState.state.reported.enable ? "green": "red" },
      { key: 'heating', label: 'Heating',
        value: acState.state.reported.heat_cmd },
    ];
    return (
      <Segment textAlign='center'>
        <Header>Current Status</Header>
        <Statistic.Group items={firstRow} widths='two' />
        <Statistic.Group items={secondRow} widths='two' size='mini' />
      </Segment>
    );
    /*
    return (
      <Segment textAlign='center'>
        <Header>Current Status</Header>
	<Progress progress='value' 
                  value={acState.state.reported.current_set_t} />
        <Progress progress='value' 
                  value={acState.state.reported.current_t.toFixed(1)}
                  active={acState.state.reported.heat_cmd === "on"} />
      </Segment>
    );
    */
  } else {
    return (
      <Segment loading>
        <Header>Loading status...</Header>
      </Segment>
    );
  }
}

function IntInput(props) {
  return (
    <Input type='text' action value={props.value} labelPosition='left' fluid>
      {props.label ? (<Label basic>{props.label}</Label>) : ""}
      <input />
      <Button icon='plus' onClick={(ev) => props.onChange(ev, {value: props.value + 1})} />
      <Button icon='minus' onClick={(ev) => props.onChange(ev, {value: props.value - 1})} />
    </Input>
  );
}

function Controls() {
  const [acState, setAcState] = useState({});

  useEffect(() => {
    function handleStatusChange(status) {
      setAcState(status);
    };
    API.subscribe(handleStatusChange);
    return function cleanup() {
      API.unsubscribe(handleStatusChange);
    };
  });

  function updateAcState(delta) {
    console.log(delta);
    API.update(delta);
  };

  function setOverride(min) {
    const override_ex = acState.timestamp + (min * 60);
    updateAcState({override_ex});
  }
  function overrideActive(s, e) {
    const sec_left = (acState.state.desired.override_ex - acState.timestamp);
    const min_left = sec_left / 60;
    return (min_left > s && min_left <= e);
  }

  if (!("state" in acState)) {
    return (<Segment color="yellow">Loading...</Segment>);
  }

  return (
    <Segment color="green">
      <Grid columns={3} divided stackable>
        <Grid.Column>
          <h3>Standard</h3>
          <Checkbox toggle label="Enable heat" 
                    checked={acState.state.desired.enable} 
                    onChange={(ev, d) => updateAcState({enable: d.checked})} />
          <IntInput label="Default Temp" 
                    value={acState.state.desired.default_t} 
                    onChange={(ev, d) => updateAcState({default_t: parseInt(d.value)})} />
        </Grid.Column>
        <Grid.Column>
          <h3>Override</h3>
          <IntInput label="Override Temp" 
                    value={acState.state.desired.override_t} 
                    onChange={(ev, d) => updateAcState({override_t: parseInt(d.value)})} />
          <Button.Group compact fluid>
            <Button onClick={() => setOverride(30)} active={overrideActive(0, 30)}>
              30 min
            </Button>
            <Button onClick={() => setOverride(60)} active={overrideActive(30, 60)}>1 hr</Button>
            <Button onClick={() => setOverride(120)} active={overrideActive(60, 120)}>2 hrs</Button>
            <Button onClick={() => setOverride(240)} active={overrideActive(120, 240)}>4 hrs</Button>
            <Button onClick={() => setOverride(-1)}>Cancel</Button>
          </Button.Group>
        </Grid.Column>
        <Grid.Column>
          <h3>Schedule</h3>
          <Input disabled type='number' label={{ basic: true, content: 'Temp' }} labelPosition='left' />
        </Grid.Column>
      </Grid>
    </Segment>
  );
}


function Signin() {
  const [accessKey, setAccessKey] = useState();
  const [requesting, setRequesting] = useState(false);
  const [responseState, setResponseState] = useState();

  function doSignin() {
    setRequesting(true);
    API.signin(accessKey)
       .then((state) => {
         console.log(state);
         setRequesting(false);
	 if (state.state === 'OK') {
           setResponseState('OK');
         } else {
           setResponseState(state.msg);
         }
       });
  };

  var icon = 'arrow right';
  if (responseState === 'OK') {
    icon = 'check';
  } else if (responseState !== undefined) {
    icon = 'redo';
  }

  return (
    <Segment color='blue'>
      <Header>Sign in to enable control</Header>
      <Input action={{ icon: icon, color: 'blue',
                       disabled: requesting, loading: requesting,
                       onClick: doSignin }}
             onChange={(ev, t) => { setAccessKey(t.value); }}
             placeholder='Access key...' />
    </Segment>
  );
}

// TODO:
// - make control segment
// - App() should check-auth and display appropriate segment
// - Signin should somehow signal to App when it needs to re-run check-auth


function App() {
  const control = (API.isAuth() ? <Controls /> : <Signin />);

  return (
    <Container>
      <Header as='h2'>&#x2668;&#xfe0f; AC Heater Control</Header>
      <Segment.Group>
        <AcStatus />
        {control}
      </Segment.Group>
    </Container>
  );
}

export default App;
