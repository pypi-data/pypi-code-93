# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited

from __future__ import print_function
from yoctools import *

import codecs


class Cdk(Command):
    common = True
    helpSummary = "Generate current solution SDK"
    helpUsage = """
%prog
"""
    helpDescription = """
generate current solution SDK.
"""

    # def _Options(self, p):
    #     p.add_option('-a', '--all',
    #                  dest='show_all', action='store_true',
    #                  help='show the complete list of commands')

    def defines_out(self, defines={}):
        text = ''
        if type(defines) == dict:
            for k, v in defines.items():
                if type(v) == str:
                    text += '{}="{}";'.format(k, v)
                else:
                    text += '{}={};'.format(k, v)
        return text

    def optimize_out(self, ccflags=[]):
        text = '-Os'
        if len(ccflags) > 0:
            for a in ccflags:
                if a.startswith('-O'):
                    text = a  # use last one
        return text
    def hard_float_out(self, linkflags=[]):
        if len(linkflags) > 0:
            if '-mhard-float' in linkflags:
              return 'yes'
        return 'no'

    def Execute(self, opt, args):
        def str_convert(text):
            if sys.version_info.major == 2:
                if type(text) == unicode:
                    text = text.encode('utf8')
            if type(text) != str:
                text = str(text)
            return text

        yoc = YoC()
        solution = yoc.getSolution()
        if not solution:
            put_string("The current directory is not a solution!", level='warning')
        else:
            packages = ''
            for c in solution.components:
                if c.type != 'solution':
                    packages += '    <Package ID="%s" Version="%s" IsBasic="false"/>\n' % (
                        c.name, c.version)

            boardname = 'None'
            boardversion = 'None'
            if solution.board_component:
                boardname = solution.board_component.name
                boardversion = solution.board_component.version

            text = temp.format(name=solution.solution_component.name,
                               description=str_convert(
                                   solution.solution_component.description),
                               chip_name=solution.chip_component.name,
                               chip_version=solution.chip_component.version,
                               board_name=boardname,
                               board_version=boardversion,
                               packages=packages,
                               cpu_name=solution.cpu_name,
                              #  usehardfloat=self.hard_float_out(solution.LINKFLAGS),
                               defines=self.defines_out(solution.defines),
                               optimize=self.optimize_out(solution.CCFLAGS),
                               CCFLAGS=' '.join(solution.CCFLAGS),
                               LINKFLAGS=' '.join(solution.LINKFLAGS),
                               ld_script=solution.ld_script,
                               algorithms_path=solution.algorithms_path)


            if not os.path.exists(os.path.join(solution.solution_component.path, 'script')):
              try:
                  shutil.copytree(
                      '/usr/local/lib/yoctools/script',
                      os.path.join(solution.solution_component.path, 'script'))
              except Exception as ex:
                  pass
              if solution.board_component:
                  generate_flash_init(os.path.join(solution.board_component.path, 'configs/config.yaml'),
                                      os.path.join(solution.solution_component.path, 'script/flash.init'))

            try:
                filename = os.path.join(solution.solution_component.path,
                                        'project.cdkproj')
                with codecs.open(filename, 'w', 'UTF-8') as f:
                    if sys.version_info.major == 2:
                        if type(text) == str:
                            text = text.decode('UTF-8')
                    f.write(text)
                    put_string("Generate cdk project.cdkproj success.", level='info')
                return True
            except Exception as ex:
                put_string("Generate %s file failed." % filename, level='warning')


temp = '''<?xml version="1.0" encoding="UTF-8"?>
<Project Name="{name}" Version="1">
  <Description>{description}</Description>
  <MonitorProgress>
    <FlashOperate>230</FlashOperate>
    <DebugLaunch>118</DebugLaunch>
  </MonitorProgress>
  <Chips>
    <Chip ID="{chip_name}" Version="{chip_version}" IsBasic="false"/>
  </Chips>
  <Boards>
    <Board ID="{board_name}" Version="{board_version}" IsBasic="false"/>
  </Boards>
  <Packages>
{packages}  </Packages>
  <MergedToYaml>yes</MergedToYaml>
  <DebugSessions>
    <watchExpressions/>
    <memoryExpressions>;;;</memoryExpressions>
    <statistics>;;MHZ;</statistics>
    <peripheralTabs/>
    <WatchDisplayFormat>0</WatchDisplayFormat>
    <LocalDisplayFormat>0</LocalDisplayFormat>
    <debugLayout/>
    <memoryTabColSizeExpressions>100:8;100:8;100:8;100:8;</memoryTabColSizeExpressions>
  </DebugSessions>
  <BuildConfigs>
    <BuildConfig Name="BuildSet">
      <Target>
        <ROMBank Selected="1">
          <ROM1>
            <InUse>yes</InUse>
            <Start>0x20000000</Start>
            <Size>0x1000</Size>
          </ROM1>
          <ROM2>
            <InUse>no</InUse>
            <Start/>
            <Size/>
          </ROM2>
          <ROM3>
            <InUse>no</InUse>
            <Start/>
            <Size/>
          </ROM3>
          <ROM4>
            <InUse>no</InUse>
            <Start/>
            <Size/>
          </ROM4>
          <ROM5>
            <InUse>no</InUse>
            <Start/>
            <Size/>
          </ROM5>
        </ROMBank>
        <RAMBank>
          <RAM1>
            <InUse>no</InUse>
            <Start>0x20001000</Start>
            <Size>0x1000</Size>
            <Init>yes</Init>
          </RAM1>
          <RAM2>
            <InUse>no</InUse>
            <Start/>
            <Size/>
            <Init>yes</Init>
          </RAM2>
          <RAM3>
            <InUse>no</InUse>
            <Start/>
            <Size/>
            <Init>yes</Init>
          </RAM3>
          <RAM4>
            <InUse>no</InUse>
            <Start/>
            <Size/>
            <Init>yes</Init>
          </RAM4>
          <RAM5>
            <InUse>no</InUse>
            <Start/>
            <Size/>
            <Init>yes</Init>
          </RAM5>
        </RAMBank>
        <CPU>{cpu_name}</CPU>
        <UseMiniLib>yes</UseMiniLib>
        <Endian>little</Endian>
        <UseEnhancedLRW>no</UseEnhancedLRW>
        <UseContinueBuild>no</UseContinueBuild>
        <UseSemiHost>no</UseSemiHost>
      </Target>
      <Output>
        <OutputName>$(ProjectName)</OutputName>
        <Type>Executable</Type>
        <CreateHexFile>yes</CreateHexFile>
        <CreateBinFile>no</CreateBinFile>
        <Preprocessor>no</Preprocessor>
        <Disassmeble>yes</Disassmeble>
        <CallGraph>no</CallGraph>
        <Map>yes</Map>
      </Output>
      <User>
        <BeforeCompile>
          <RunUserProg>no</RunUserProg>
          <UserProgName/>
        </BeforeCompile>
        <BeforeMake>
          <RunUserProg>yes</RunUserProg>
          <UserProgName>"$(ProjectPath)/script/pre_build.sh"</UserProgName>
        </BeforeMake>
        <AfterMake>
          <RunUserProg>yes</RunUserProg>
          <UserProgName>"$(ProjectPath)/script/aft_build.sh"</UserProgName>
        </AfterMake>
      </User>
      <Compiler>
        <Define>{defines}</Define>
        <Undefine/>
        <Optim>Optimize ({optimize})</Optim>
        <DebugLevel>Default (-g)</DebugLevel>
        <IncludePath>$(ProjectPath)/src;$(ProjectPath)/include</IncludePath>
        <OtherFlags>{CCFLAGS}</OtherFlags>
        <Verbose>no</Verbose>
        <Ansi>no</Ansi>
        <Syntax>no</Syntax>
        <Pedantic>no</Pedantic>
        <PedanticErr>no</PedanticErr>
        <InhibitWarn>no</InhibitWarn>
        <AllWarn>yes</AllWarn>
        <WarnErr>no</WarnErr>
        <OneElfS>no</OneElfS>
        <Fstrict>no</Fstrict>
      </Compiler>
      <Asm>
        <Define>{defines}</Define>
        <Undefine/>
        <IncludePath>$(ProjectPath)/src;$(ProjectPath)/include</IncludePath>
        <OtherFlags/>
        <DebugLevel>gdwarf2</DebugLevel>
      </Asm>
      <Linker>
        <Garbage>yes</Garbage>
        <LDFile>$(ProjectPath)/gcc_eflash.ld</LDFile>
        <LibName/>
        <LibPath/>
        <OtherFlags>{LINKFLAGS}</OtherFlags>
        <AutoLDFile>no</AutoLDFile>
        <LinkType/>
      </Linker>
      <Debug>
        <LoadApplicationAtStartup>yes</LoadApplicationAtStartup>
        <Connector>ICE</Connector>
        <StopAt>yes</StopAt>
        <StopAtText>main</StopAtText>
        <InitFile>$(ProjectPath)/script/gdbinit</InitFile>
        <AutoRun>yes</AutoRun>
        <ResetType>Hard Reset</ResetType>
        <SoftResetVal/>
        <ResetAfterLoad>no</ResetAfterLoad>
        <Dumpcore>no</Dumpcore>
        <DumpcoreText>$(ProjectPath)/$(ProjectName).cdkcore</DumpcoreText>
        <ConfigICE>
          <IP>localhost</IP>
          <PORT>1025</PORT>
          <CPUNumber>0</CPUNumber>
          <Clock>12000</Clock>
          <Delay>10</Delay>
          <WaitReset>500</WaitReset>
          <DDC>yes</DDC>
          <TRST>no</TRST>
          <DebugPrint>no</DebugPrint>
          <Connect>Normal</Connect>
          <ResetType>Soft Reset</ResetType>
          <SoftResetVal>0</SoftResetVal>
          <RTOSType>Bare Metal</RTOSType>
          <DownloadToFlash>yes</DownloadToFlash>
          <ResetAfterConnect>no</ResetAfterConnect>
          <GDBName/>
          <GDBServerType>Local</GDBServerType>
          <OtherFlags/>
        </ConfigICE>
        <ConfigSIM>
          <SIMTarget>soccfg/cskyv2/rhea802.xml</SIMTarget>
          <OtherFlags/>
          <NoGraphic>yes</NoGraphic>
          <Log>no</Log>
          <SimTrace>no</SimTrace>
        </ConfigSIM>
      </Debug>
      <Flash>
        <InitFile>$(ProjectPath)/script/flash.init</InitFile>
        <Erase>Erase Sectors</Erase>
        <Algorithms Path="">{algorithms_path}</Algorithms>
        <Program>yes</Program>
        <Verify>yes</Verify>
        <ResetAndRun>no</ResetAndRun>
        <ResetType>Soft Reset</ResetType>
        <SoftResetVal/>
        <External>no</External>
        <Command/>
        <Arguments/>
      </Flash>
    </BuildConfig>
  </BuildConfigs>
  <Dependencies Name="BuildSet"/>
  <PackPathes>$(ProjectPath)/../../components|$(ProjectPath)/../../boards|$(ProjectPath)/Boards|$(ProjectPath)/Chips|$(ProjectPath)/Packages</PackPathes>
</Project>
'''


def generate_flash_init(config_yaml, filename):
    text = '''

{downloads} '''
    v = yaml_load(config_yaml)
    cmd = 'download ihex verify=no $(ProjectPath)/generated/{name}.hex'
    downloads = []
    for k in v['partitions']:
        # put_string(k)
        f = cmd.format(name=k['name'])
        downloads.append(f)

    downloads = '\n'.join(downloads)
    # put_string(s)
    text = text.format(downloads=downloads)
    try:
        with codecs.open(filename, 'w', 'UTF-8') as f:
            f.write(text)
        return True
    except Exception as ex:
        put_string("Generate %s file failed." % filename, level='warning')