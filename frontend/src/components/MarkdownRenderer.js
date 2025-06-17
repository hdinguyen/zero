import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';

const MarkdownRenderer = ({ content, isUser = false }) => {
  const customComponents = {
    // Custom paragraph styling
    p: ({ children }) => (
      <p className="mb-2 last:mb-0 text-sm font-normal leading-normal">
        {children}
      </p>
    ),
    
    // Custom heading styles
    h1: ({ children }) => (
      <h1 className="text-lg font-bold mb-2 text-current">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-base font-bold mb-2 text-current">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-sm font-bold mb-1 text-current">
        {children}
      </h3>
    ),
    
    // Custom list styles
    ul: ({ children }) => (
      <ul className="list-disc list-inside mb-2 ml-2 text-sm">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside mb-2 ml-2 text-sm">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="mb-1 text-current">
        {children}
      </li>
    ),
    
    // Custom code block styling
    code: ({ inline, className, children, ...props }) => {
      const codeString = Array.isArray(children) ? children.join('').trim() : String(children).trim();
      if (inline) {
        return (
          <code className={`px-1 py-0.5 rounded text-xs font-mono ${
            isUser 
              ? 'bg-blue-600 text-blue-100' 
              : 'bg-gray-200 text-gray-800'
          }`} {...props}>
            {codeString}
          </code>
        );
      }
      // Extract language if present
      const match = /language-(\w+)/.exec(className || '');
      return (
        <div className="my-2">
          <pre className={`p-3 rounded-lg overflow-x-auto text-xs font-mono ${
            isUser 
              ? 'bg-blue-600 text-blue-100' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            <code className={className || ''} {...props}>
              {codeString}
            </code>
          </pre>
        </div>
      );
    },
    
    // Custom blockquote styling
    blockquote: ({ children }) => (
      <blockquote className={`border-l-4 pl-3 my-2 text-sm italic ${
        isUser 
          ? 'border-blue-300 text-blue-100' 
          : 'border-gray-300 text-gray-600'
      }`}>
        {children}
      </blockquote>
    ),
    
    // Custom table styling
    table: ({ children }) => (
      <div className="overflow-x-auto my-2">
        <table className="min-w-full text-xs border-collapse">
          {children}
        </table>
      </div>
    ),
    th: ({ children }) => (
      <th className={`border p-2 text-left font-medium ${
        isUser 
          ? 'border-blue-300 bg-blue-600' 
          : 'border-gray-300 bg-gray-100'
      }`}>
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className={`border p-2 ${
        isUser 
          ? 'border-blue-300' 
          : 'border-gray-300'
      }`}>
        {children}
      </td>
    ),
    
    // Custom image styling with error handling
    img: ({ src, alt, title }) => (
      <div className="my-2">
        <img 
          src={src} 
          alt={alt || 'Image'} 
          title={title}
          className="max-w-full h-auto rounded-lg shadow-sm"
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextElementSibling.style.display = 'block';
          }}
        />
        <div 
          style={{ display: 'none' }}
          className={`p-3 rounded-lg text-xs ${
            isUser 
              ? 'bg-blue-600 text-blue-200' 
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          🖼️ Image could not be loaded: {alt || src}
        </div>
      </div>
    ),
    
    // Custom link styling
    a: ({ href, children }) => (
      <a 
        href={href} 
        target="_blank" 
        rel="noopener noreferrer"
        className={`underline hover:no-underline ${
          isUser 
            ? 'text-blue-200 hover:text-white' 
            : 'text-blue-600 hover:text-blue-800'
        }`}
      >
        {children}
      </a>
    ),
    
    // Custom horizontal rule
    hr: () => (
      <hr className={`my-3 border-0 h-px ${
        isUser 
          ? 'bg-blue-300' 
          : 'bg-gray-300'
      }`} />
    ),
  };

  return (
    <div className="markdown-content">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={customComponents}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer; 