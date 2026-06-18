export interface SectionProps {
  id?: string;
  className?: string;
}

export interface LinkItem {
  label: string;
  href: string;
}

export interface ImageAsset {
  src: string;
  alt: string;
  width?: number;
  height?: number;
}
