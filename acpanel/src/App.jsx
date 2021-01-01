import React, { useState, useEffect } from 'react';
import { Button, Container, Header, Label } from 'semantic-ui-react';
//import './App.css';
import API from './api';


function App() {
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

  var labels = (<div />);
  if ("state" in acState) {
    labels = (<div>
      <Label>Set Temp<Label.Detail>{acState.state.reported.current_set_t}</Label.Detail></Label>
      <Label>Current Temp<Label.Detail>{acState.state.reported.current_t}</Label.Detail></Label>
      <Label>Display Temp<Label.Detail>{acState.state.reported.display_t}</Label.Detail></Label>
      <Label>Enabled<Label.Detail>{acState.state.reported.enable ? "true" : "false"}</Label.Detail></Label>
      <Label>Heating<Label.Detail>{acState.state.reported.heat_cmd}</Label.Detail></Label>
    </div>);
  }

  return (
    <Container>
      <Header as='h2'>AC Heater Control</Header>
      <Button>Click me!</Button>
      {labels}
    </Container>
  );
}

export default App;
