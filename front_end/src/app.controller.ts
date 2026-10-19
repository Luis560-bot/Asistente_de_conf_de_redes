import { Controller, Get, Res } from '@nestjs/common';
import type { Response } from 'express';
import { join } from 'node:path';
import { AppService } from './app.service.js';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getIndex(@Res() res: Response): void {
    res.sendFile(join(process.cwd(), 'public', 'index.html'));
  }

  @Get('api/hello')
  getHello(): string {
    return this.appService.getHello();
  }
}
