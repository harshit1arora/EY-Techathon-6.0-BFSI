import React, { useState, useEffect } from 'react';
import { X, FileText, Image, AlertCircle, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';

interface DocumentPreviewProps {
  file: File;
  onConfirm: () => void;
  onCancel: () => void;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({ file, onConfirm, onCancel }) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const maxSize = 5 * 1024 * 1024; // 5MB
  const isOversize = file.size > maxSize;
  const isImage = file.type.startsWith('image/');
  const isPDF = file.type === 'application/pdf';

  useEffect(() => {
    if (isImage) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.onerror = () => {
        setError('Failed to load image preview');
      };
      reader.readAsDataURL(file);
    }
  }, [file, isImage]);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md bg-card border-border shadow-2xl animate-scale-in">
        <CardHeader className="flex flex-row items-center justify-between border-b border-border">
          <CardTitle className="text-lg font-semibold text-foreground">Preview Document</CardTitle>
          <Button variant="ghost" size="icon" onClick={onCancel}>
            <X className="w-5 h-5" />
          </Button>
        </CardHeader>
        
        <CardContent className="p-4 space-y-4">
          {/* Preview Area */}
          <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center overflow-hidden">
            {isImage && preview ? (
              <img src={preview} alt="Preview" className="max-w-full max-h-full object-contain" />
            ) : isPDF ? (
              <div className="flex flex-col items-center justify-center text-muted-foreground">
                <FileText className="w-16 h-16 mb-2" />
                <span className="text-sm">PDF Document</span>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-muted-foreground">
                <FileText className="w-16 h-16 mb-2" />
                <span className="text-sm">{file.type || 'Unknown file type'}</span>
              </div>
            )}
          </div>

          {/* File Info */}
          <div className="space-y-2 bg-muted/50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">File Name</span>
              <span className="text-sm font-medium text-foreground truncate max-w-[200px]">{file.name}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Size</span>
              <span className={`text-sm font-medium ${isOversize ? 'text-destructive' : 'text-foreground'}`}>
                {formatFileSize(file.size)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Type</span>
              <span className="text-sm font-medium text-foreground">{file.type || 'Unknown'}</span>
            </div>
          </div>

          {/* Validation Messages */}
          {isOversize && (
            <div className="flex items-center space-x-2 text-destructive bg-destructive/10 p-3 rounded-lg">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">File exceeds 5MB limit. Please choose a smaller file.</span>
            </div>
          )}

          {error && (
            <div className="flex items-center space-x-2 text-destructive bg-destructive/10 p-3 rounded-lg">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-end space-x-3 border-t border-border p-4">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button 
            onClick={onConfirm} 
            disabled={isOversize}
            className="bg-primary hover:bg-primary/90"
          >
            <Check className="w-4 h-4 mr-2" />
            Upload
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default DocumentPreview;
