import React from 'react';
import TextInputField from './TextInputField';

const TestPage = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Teste de Componentes</h1>
      <div style={{ marginBottom: '20px' }}>
        <h2>Teste TextInputField - Texto Fonte</h2>
        <TextInputField
          label='Texto Fonte (Original)'
          placeholder='Digite ou carregue o texto original aqui.'
          required={true}
          value=''
          onChange={() => {}}
          disabled={false}
        />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h2>Teste TextInputField - Texto Alvo</h2>
        <TextInputField
          label='Texto Alvo (Simplificado)'
          placeholder='Digite ou carregue o texto simplificado aqui.'
          required={true}
          value=''
          onChange={() => {}}
          disabled={false}
        />
      </div>
    </div>
  );
};

export default TestPage;
