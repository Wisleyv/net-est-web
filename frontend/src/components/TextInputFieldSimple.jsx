import React, { useState } from 'react';

const TextInputField = ({
  label,
  placeholder,
  required = false,
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <div className='space-y-3'>
      <label className='block text-sm font-medium text-gray-700'>
        {label} {required && <span className='text-red-500'>*</span>}
      </label>
      <textarea
        value={value || ''}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className='w-full h-40 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-gray-50 disabled:cursor-not-allowed'
      />
      <div className='text-xs text-gray-500'>
        {value ? `${value.length} caracteres` : '0 caracteres'}
      </div>
    </div>
  );
};

export default TextInputField;
