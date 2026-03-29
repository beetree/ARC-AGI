#!/usr/bin/pike
/* Copyright (C) 2004  Jeroen Dekkers <jeroen@dekkers.cx>
   Copyright (C) 2004  Ben Asselstine <benasselstine@canada.com>
   Copyright (C) 2006  Ying-Chun Liu <grandpaul@gmail.com>

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License
   as published by the Free Software Foundation; either version 2
   of the License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA */

/* test case generator 1 */

import Stdio;

int crc32(string data, int|void shiftRegister) {
  int i, j;
  int nextByte, mask;

  shiftRegister = (~shiftRegister) & 0x0FFFFFFFF;
  for (i=0; i<strlen(data); i++) {
    nextByte = data[i] & 0x000000FF;
    shiftRegister = (shiftRegister ^ nextByte) & (0x0FFFFFFFF);
    for (j = 7; j >= 0; j--) {
      mask = (-(shiftRegister & 1)) & (0x0FFFFFFFF);
      shiftRegister = (shiftRegister >> 1) ^ (0x0EDB88320 & mask);
    }
  }
  return ((~shiftRegister) & 0x0FFFFFFFF);
}

int crc32_file(Stdio.File file1) {
  int currentpos;
  int shiftRegister=0;
  string data;

  currentpos = file1->tell();

  file1->seek(0);

  while (1) {
    data = file1->read(1024*8);
    if (data == 0 || strlen(data)==0) {
      break;
    }
    shiftRegister = crc32(data, shiftRegister);
  }

  file1->seek(currentpos);
  return shiftRegister;
}

string int2bin16 (int d) {
  string ret;
  ret=sprintf("%c%c",
	      d%256,
	      (d/256)%256);
  return ret;
}

string int2bin32 (int d) {
  string ret;
  ret=sprintf("%c%c%c%c",
	      d%256,
	      (d/256)%256,
	      (d/256/256)%256,
	      (d/256/256/256)%256);
  return ret;
}

int addfile(string filename1,Stdio.File rarfile) {
  Stdio.File datafile = Stdio.File();
  Stdio.Stat datafile_stat;
  int datafile_crc32,tmp1;
  mapping(string:int) datafile_mtime;
  string datafile_header;
  if (datafile->open(filename1,"r")==0) {
    return 0;
  }
  datafile_stat = datafile->stat();
  datafile_mtime = localtime(datafile_stat->mtime);
  datafile_crc32 = ((crc32_file(datafile)) & 0x0ffffffff);
  /* header: type, flags */
  datafile_header = "\x74\0\x80";
  /* header: header size */
  tmp1 = 32+strlen(filename1);
  datafile_header = datafile_header + int2bin16(tmp1);
  /* header: comp. size, uncomp. size */
  tmp1 = datafile_stat->size;
  datafile_header = datafile_header + int2bin32(tmp1);
  datafile_header = datafile_header + int2bin32(tmp1);
  /* header: OS */
  datafile_header = datafile_header + "\0";
  /* header: File CRC */
  tmp1 = datafile_crc32;
  datafile_header = datafile_header + int2bin32(tmp1);
  /* header: time */
  tmp1 = (datafile_mtime["year"]-80);
  if (tmp1 < 0) tmp1=0;
  tmp1 = tmp1 << 25;
  tmp1 = tmp1 + ((datafile_mtime["mon"]+1)<<21);
  tmp1 = tmp1 + ((datafile_mtime["mday"])<<16);
  tmp1 = tmp1 + ((datafile_mtime["hour"])<<11);
  tmp1 = tmp1 + ((datafile_mtime["min"])<<5);
  tmp1 = tmp1 + ((datafile_mtime["sec"])>>1);
  datafile_header = datafile_header + int2bin32(tmp1);
  /* header: unp. version, method */
  datafile_header = datafile_header + "\x14\x30";
  /* header: filename size */
  tmp1 = strlen(filename1);
  datafile_header = datafile_header + int2bin16(tmp1);
  /* header: file attr. */
  datafile_header = datafile_header + "\x20\0\0\0";
  /* header: filename */
  datafile_header = datafile_header + 
    replace(filename1,"/","\\");
  /* header: crc32 */
  tmp1 = ((crc32(datafile_header)) & 0x0000ffff);
  datafile_header = int2bin16(tmp1) + datafile_header;
  rarfile->write(datafile_header);
  while (1) {
    string datatmp;
    datatmp = datafile->read(1024*8);
    if (datatmp == 0 || strlen(datatmp)==0) {
      break;
    }
    rarfile->write(datatmp);
  }
  datafile->close();
  return 1;
}

int adddir_header(string filename1,Stdio.File rarfile) {
  int tmp1;
  string datafile_header="";
  Stdio.Stat datafile_stat;
  mapping(string:int) datafile_mtime;

  /* header: type, flags */
  datafile_header = "\x74\0\xe0";
  if (has_suffix(filename1, "\\") || has_suffix(filename1,"/")) {
    filename1 = filename1[..strlen(filename1)-2];
  }

  tmp1 = 32+strlen(filename1);
  datafile_header += int2bin16(tmp1);
  datafile_header += int2bin32(0);
  datafile_header += int2bin32(0);
  datafile_header += "\0";
  datafile_header += int2bin32(0);
  datafile_stat = file_stat(filename1);
  datafile_mtime = localtime(datafile_stat->mtime);

  tmp1 = (datafile_mtime["year"]-80);
  if (tmp1 < 0) tmp1=0;
  tmp1 = tmp1 << 25;
  tmp1 = tmp1 + ((datafile_mtime["mon"]+1)<<21);
  tmp1 = tmp1 + ((datafile_mtime["mday"])<<16);
  tmp1 = tmp1 + ((datafile_mtime["hour"])<<11);
  tmp1 = tmp1 + ((datafile_mtime["min"])<<5);
  tmp1 = tmp1 + ((datafile_mtime["sec"])>>1);
  datafile_header += int2bin32(tmp1);
  datafile_header += "\x14\x30";
  tmp1 = strlen(filename1);
  datafile_header += int2bin16(tmp1);
  datafile_header += "\x10\0\0\0";
  datafile_header +=replace(filename1,"/","\\");
  tmp1 = ((crc32(datafile_header)) & 0x0000ffff);
  datafile_header = int2bin16(tmp1) + datafile_header;
  rarfile->write(datafile_header);
}

mapping(string:int) adddir_dirs=([]);
int adddir(string filename1,Stdio.File rarfile) {
  Filesystem.Traversion ft;
  string filename;
  ft = Filesystem.Traversion(filename1);
  foreach(ft; string dir; string file) {
    if (adddir_dirs[dir] != 1) {
      adddir_header(dir,rarfile);
      adddir_dirs += ([dir:1]);
    }
    filename = dir+file;
    if (is_file(filename)) {
      addfile(filename,rarfile);
    } else if (is_dir(filename)) {
      adddir_header(filename,rarfile);
    }
  }
}

int main(int argc,array(string) argv) {
  int i;
  string filename1;
  Stdio.File rarfile = Stdio.File();
	
  if ( argc < 2 ) {
    write ( "Usage: " + argv[0] + " ARCHIVE [FILE...]\n" );
    return 1;
  }
  if (rarfile->open(argv[1],"wtc")==0) {
    write("Cannot open "+argv[1]+" file\n");
    return 0;
  }
  rarfile->write("Rar!\x1a\x07\0"); /* Marker block */
  rarfile->write("\xcf\x90\x73\0\0\x0d\0\0\0\0\0\0\0"); /* Archive header */
  for (i=2 ; i<argc ; i++) {
    filename1 = argv[i];
    if (is_file(filename1)) {
      addfile(filename1,rarfile);
    } else if (is_dir(filename1)) {
      adddir(filename1,rarfile);
    }
  }
  rarfile->close();
  return 0;
}
