import { Controller, Get, Post, Body } from '@nestjs/common';
import { AppService } from './app.service.js';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('api/hello')
  getHello(): string {
    return this.appService.getHello();
  }

  @Post('api/ia')
  async IA(@Body('message') message: string): Promise<string> {
    return this.appService.getIAResponse(message);
  }
}
