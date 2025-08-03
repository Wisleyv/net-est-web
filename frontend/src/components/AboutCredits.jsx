/**
 * Componente de créditos e autoria
 */

import React, { useState } from 'react';

const AboutCredits = () => {
  const [isOpen, setIsOpen] = useState(false);

  const credits = {
    project:
      'NET-EST - Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual',
    team: [
      {
        role: 'Coordenação',
        name: 'Profa. Dra. Janine Pimentel',
        affiliation: 'PIPGLA/UFRJ e Politécnico de Leiria',
      },
      {
        role: 'Desenvolvedor Principal',
        name: 'Wisley Vilela',
        affiliation: 'Doutorando PIPGLA/UFRJ',
      },
      {
        role: 'Especialista Linguística',
        name: 'Luanny Matos de Lima',
        affiliation: 'Mestranda PIPGLA/UFRJ',
      },
      {
        role: 'Agentes Técnicos de IA',
        name: 'Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash',
        affiliation: 'mediados por GitHub Copilot',
      },
    ],
    institutions: [
      'Núcleo de Estudos de Tradução - UFRJ',
      'Politécnico de Leiria (PT)',
    ],
    license: 'MIT License',
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className='text-sm text-blue-600 hover:text-blue-800 underline'
      >
        Créditos
      </button>

      {isOpen && (
        <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
          <div className='bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto'>
            <div className='flex justify-between items-start mb-4'>
              <h2 className='text-xl font-bold text-gray-900'>
                Créditos do Projeto
              </h2>
              <button
                onClick={() => setIsOpen(false)}
                className='text-gray-400 hover:text-gray-600 text-2xl'
              >
                ×
              </button>
            </div>

            <div className='space-y-4'>
              <div>
                <h3 className='font-semibold text-gray-800 mb-2'>Projeto</h3>
                <p className='text-sm text-gray-600'>{credits.project}</p>
              </div>

              <div>
                <h3 className='font-semibold text-gray-800 mb-2'>
                  Equipe de Desenvolvimento
                </h3>
                <div className='space-y-2'>
                  {credits.team.map((member, index) => (
                    <div key={index} className='text-sm'>
                      <span className='font-medium'>{member.role}:</span>{' '}
                      {member.name}
                      <div className='text-gray-600 ml-4'>
                        ({member.affiliation})
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className='font-semibold text-gray-800 mb-2'>
                  Instituições
                </h3>
                <ul className='text-sm text-gray-600 list-disc list-inside'>
                  {credits.institutions.map((institution, index) => (
                    <li key={index}>{institution}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className='font-semibold text-gray-800 mb-2'>Licença</h3>
                <p className='text-sm text-gray-600'>
                  {credits.license} - Código aberto
                </p>
              </div>

              <div className='pt-4 border-t text-xs text-gray-500'>
                Versão 1.0.0 - Foundation Layer Implementado
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AboutCredits;
