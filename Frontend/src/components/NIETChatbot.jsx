import React, { useState } from 'react';
import NIETChatbotUI from './NIETChatbotUI';
import NIETChatbotMessages from './NIETChatbotMessages';

export default function NIETChatbot() {
  const [open, setOpen] = useState(false);

  function toggleOpen() {
    setOpen((v) => !v);
  }

  return (
    <NIETChatbotUI isOpen={open} onToggle={toggleOpen}>
      <NIETChatbotMessages />
    </NIETChatbotUI>
  );
}
